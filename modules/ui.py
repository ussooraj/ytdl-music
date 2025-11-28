import os
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel

console = Console()

def header():
    console.print(Panel.fit("[bold cyan]YT Downloader for music[/bold cyan]", style="bold magenta"))

def get_input_mode():
    console.print("\n[bold cyan]Select Input Mode:[/bold cyan]")
    console.print("1. Single YouTube URL")
    console.print("2. Playlist URL")
    console.print("3. Text File (Batch Mode)")
    console.print("4. Search (Direct Download)")
    
    choice = IntPrompt.ask("Enter your choice", choices=["1", "2", "3", "4"])
    
    mapping = {
        1: "url",
        2: "playlist",
        3: "file",
        4: "search"
    }
    return mapping[choice]

def get_user_input(mode):
    if mode == "url":
        return Prompt.ask("[green]Enter the YouTube URL[/green]")
    elif mode == "playlist":
        return Prompt.ask("[green]Enter the Playlist URL[/green]")
    elif mode == "file":
        path = Prompt.ask("[green]Enter the path to the .txt file[/green]")
        if not os.path.exists(path):
            console.print(f"[red]Error: File {path} not found![/red]")
            exit()
        return path
    elif mode == "search":
        query = Prompt.ask("[green]Enter Song Name / Artist[/green]")
        return f"ytsearch1:{query}"


def get_codec_preference():
    """
    Asks user for Audio Codec and Quality.
    Returns:
        dict: {'codec': str, 'quality': str}
    """
    console.print("\n[bold cyan]Select Audio Codec:[/bold cyan]")
    console.print("1. Opus (Default - Best Quality/Compression)")
    console.print("2. MP3  (Universal Compatibility)")
    console.print("3. FLAC (Lossless - Large File Size)")
    console.print("4. M4A  (AAC - Good for Apple Devices)")

    choice = IntPrompt.ask("Enter choice", choices=["1", "2", "3", "4"], default=1)

    codec_map = {1: 'opus', 2: 'mp3', 3: 'flac', 4: 'm4a'}
    selected_codec = codec_map[choice]

    # '0' is the highest quality available
    quality_setting = '0' 

    if selected_codec == 'mp3':
        console.print("\n[bold cyan]Select MP3 Quality:[/bold cyan]")
        console.print("1. 320 kbps (CBR - High Quality)")
        console.print("2. 192 kbps (VBR - Balanced)")
        console.print("3. Best Possible (VBR ~0)")
        
        q_choice = IntPrompt.ask("Choice", choices=["1", "2", "3"], default=3)
        if q_choice == 1:
            quality_setting = '320'
        elif q_choice == 2:
            quality_setting = '192'
        else:
            quality_setting = '0'

    return {
        'codec': selected_codec, 
        'quality': quality_setting
    }

def get_save_directory():
    """
    Asks user for download directory. Defaults to Music folder.
    """
    console.print("\n[bold cyan]Download Directory:[/bold cyan]")
    default_dir = os.path.join(os.path.expanduser("~"), "Music")    
    path = Prompt.ask("Enter path (Leave empty for Music folder)", default=default_dir)    
    
    full_path = os.path.expanduser(path)    # Expand '~' if entered

    # Create directory if it doesn't exist
    if not os.path.exists(full_path):
        create = Confirm.ask(f"[yellow]Directory '{full_path}' does not exist. Create it?[/yellow]")
        if create:
            try:
                os.makedirs(full_path)
                console.print(f"[green]Created directory: {full_path}[/green]")
            except OSError as e:
                console.print(f"[red]Error creating directory: {e}[/red]")
                return default_dir
        else:
            return default_dir

    return full_path