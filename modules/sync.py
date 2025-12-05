import os
import json
from rich.console import Console
from .downloader import run_download, fetch_ids
from .manifest import load_manifest, save_manifest, ManifestUpdater

console = Console()
CONFIG_FILE = "playlists.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"playlists": []}
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"playlists": []}

def save_config(config):
    if not os.path.exists(CONFIG_FILE):
        console.print(f"[bold green]Initializing {CONFIG_FILE}...[/bold green]")
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def update_config(url, directory, audio_settings):
    """
    Adds a new playlist or updates an existing one in the playlists.json file.
    Returns the playlist entry.
    """
    config = load_config()
    existing = config.get('playlists', [])
    
    entry = {
        "url": url,
        "directory": directory,
        "audio_settings": audio_settings
    }

    found = False
    for p in existing:
        if p['url'] == url:
            p['directory'] = directory
            p['audio_settings'] = audio_settings
            found = True
            console.print(f"[yellow]Updated existing playlist config.[/yellow]")
            break
    
    if not found:
        config.setdefault('playlists', []).append(entry)
        console.print(f"[bold green]Playlist added to sync config![/bold green]")
    
    save_config(config)
    return entry

def sync_playlist(playlist_config, progress_hook=None):
    url = playlist_config['url']
    directory = playlist_config['directory']
    codec_data = playlist_config['audio_settings']
    
    console.print(f"\n[bold cyan]Syncing playlist: {url}[/bold cyan]")
    console.print(f"[dim]Target: {directory}[/dim]")

    if not os.path.exists(directory):
        os.makedirs(directory)

    online_items = fetch_ids(url) # {id: title}

    if not online_items:
        console.print("[red]Could not fetch playlist items. Aborting sync for this playlist.[/red]")
        return
    manifest = load_manifest(directory) # {id: filename}

    online_ids = set(online_items.keys())
    local_ids = set(manifest.keys())

    to_add = online_ids - local_ids
    to_remove = local_ids - online_ids

    if to_remove:
        console.print("\n[yellow]Removing {len(to_remove)} items...[/yellow]")
        for vid_id in to_remove:
            filename = manifest[vid_id]
            file_path = os.path.join(directory, filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    console.print(f"[red]Deleted:[/red] {filename}")
                except OSError as e:
                    console.print(f"[red]Error deleting {filename}: {e}[/red]")
            
            base_name = os.path.splitext(filename)[0]
            for ext in ['.json', '.jpg', '.png', '.webp']:
                extra_path = os.path.join(directory, base_name + ext)
                if os.path.exists(extra_path):
                    try:
                        os.remove(extra_path)
                    except: pass

            del manifest[vid_id]
        save_manifest(directory, manifest)

    if to_add:
        console.print(f"\n[green]Adding {len(to_add)} new items...[/green]")
        
        urls_to_download = [f"https://www.youtube.com/watch?v={vid_id}" for vid_id in to_add]
        
        updater = ManifestUpdater(directory, codec_data)
        
        hooks = [updater.hook]
        if progress_hook:
            hooks.append(progress_hook)

        run_download(urls_to_download, codec_data, directory, hooks)

    if not to_add and not to_remove:
        console.print("\n[green]Playlist is already up to date.[/green]")

    console.print(f"\n[bold green]Sync complete for {url}[/bold green]\n")
