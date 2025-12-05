import os
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from modules.ui import (
    header,
    get_input_mode, 
    get_user_input, 
    get_codec_preference, 
    get_save_directory,
    console
)
from modules.downloader import run_download

def progress_bar():
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    )

def main():
    console.clear()
    header()

    mode = get_input_mode()

    if mode == "sync":
        from modules.sync import load_config, sync_playlist
        
        config = load_config()
        playlists = config.get('playlists', [])
        
        if not playlists:
            console.print("[yellow]No synced playlists found. Use 'Download / Sync Playlist' to add one.[/yellow]")
            return

        console.print(f"\n[bold green]Starting Sync for {len(playlists)} playlists...[/bold green]")
        
        with progress_bar() as progress:
            download_task = progress.add_task("[cyan]Initializing...", total=100)

            def progress_hook(d):
                if d['status'] == 'downloading':
                    try:
                        p = d.get('_percent_str', '0%').replace('%','')
                        progress.update(download_task, completed=float(p), description=f"[cyan]Downloading: {d.get('filename', 'file')}")
                    except:
                        pass
                elif d['status'] == 'finished':
                    progress.update(download_task, description="[green]Processing Audio/Metadata...[/green]")

            for pl in playlists:
                sync_playlist(pl, progress_hook)

        console.print("\n[bold green]Sync Operations Complete![/bold green]")
        return

    elif mode == "playlist":
        from modules.sync import update_config, sync_playlist
        
        url = get_user_input("playlist")
        save_path = get_save_directory()
        audio_settings = get_codec_preference()
        
        new_entry = update_config(url, save_path, audio_settings)

        console.print(f"\n[bold green]Starting Download/Sync...[/bold green]")
        
        with progress_bar() as progress:
            download_task = progress.add_task("[cyan]Initializing...", total=100)

            def progress_hook(d):
                if d['status'] == 'downloading':
                    try:
                        p = d.get('_percent_str', '0%').replace('%','')
                        progress.update(download_task, completed=float(p), description=f"[cyan]Downloading: {d.get('filename', 'file')}")
                    except:
                        pass
                elif d['status'] == 'finished':
                    progress.update(download_task, description="[green]Processing Audio/Metadata...[/green]")

            sync_playlist(new_entry, progress_hook)
            
        console.print("\n[bold green]All Operations Complete![/bold green]")
        return

    raw_input = get_user_input(mode)
    audio_settings = get_codec_preference()
    save_path = get_save_directory()

    urls = []
    if mode == "file":
        if os.path.exists(raw_input):
            with open(raw_input, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
    else:
        urls = [raw_input]

    console.print(f"\n[bold green]Starting Download...[/bold green]")
    
    with progress_bar() as progress:
        download_task = progress.add_task("[cyan]Initializing...", total=100)

        def progress_hook(d):
            if d['status'] == 'downloading':
                # Calculate percentage
                try:
                    p = d.get('_percent_str', '0%').replace('%','')
                    progress.update(download_task, completed=float(p), description=f"[cyan]Downloading: {d.get('filename', 'file')}")
                except:
                    pass
            elif d['status'] == 'finished':
                progress.update(download_task, description="[green]Processing Audio/Metadata...[/green]")

        run_download(urls, audio_settings, save_path, progress_hook)

    console.print("\n[bold green]All Operations Complete![/bold green]")

if __name__ == "__main__":
    main()