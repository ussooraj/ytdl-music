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

def main():
    # --- UI PHASE ---
    os.system('cls' if os.name == 'nt' else 'clear') # Clean start
    header()

    mode = get_input_mode()
    raw_input = get_user_input(mode)
    audio_settings = get_codec_preference()
    save_path = get_save_directory()

    # --- PREPARE DATA ---
    urls = []
    if mode == "file":
        if os.path.exists(raw_input):
            with open(raw_input, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
    else:
        urls = [raw_input]

    # --- EXECUTION PHASE ---
    console.print(f"\n[bold green]Starting Download...[/bold green]")
    
    # Create the Progress Bar Context
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        
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