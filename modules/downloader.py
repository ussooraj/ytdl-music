import yt_dlp
import os
import glob
from .utils import rm_images

class MyLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): print(f"\n[Error] {msg}")

def ydl_opts(codec_data, save_path, progress_hook):
    codec = codec_data['codec']
    quality = codec_data['quality']

    opts = {
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'format': 'bestaudio/best',

        'sponsorblock_remove': ['sponsor', 'intro', 'outro', 'selfpromo', 'interaction', 'music_offtopic'],
        # 'concurrent_fragment_downloads': 4,

        'cookiesfrombrowser': ('firefox',), # change to prefered browser (make sure youtube is logged in)
        
        'writethumbnail': True,
        'write_all_thumbnails': False,
        'write_playlist_metafiles': False, 
        
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec,
                'preferredquality': quality,
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
            {
                'key': 'EmbedThumbnail',
            },
        ],
        
        'logger': MyLogger(),
        'progress_hooks': progress_hook if isinstance(progress_hook, list) else [progress_hook],
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    return opts

def fetch_ids(playlist_url):
    """
    Fetches video IDs and titles from the playlist URL.
    Returns a dict: {video_id: title}
    """
    opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
    }
    items = {}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            result = ydl.extract_info(playlist_url, download=False)
            if 'entries' in result:
                for entry in result['entries']:
                    if entry:
                        items[entry['id']] = entry.get('title', 'Unknown Title')
    except Exception as e:
        print(f"[Error] Error fetching playlist info: {e}")
    return items

def run_download(urls, codec_data, save_path, progress_hook):
    options = ydl_opts(codec_data, save_path, progress_hook)
    
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download(urls)
        rm_images(save_path)
            
    except Exception as e:
        print(f"Critical Error: {e}")