import yt_dlp
import os
import glob

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
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    return opts

def rm_images(save_path):
    """Removes all .jpg, .png, and .webp files from the directory."""
    for ext in ('*.jpg', '*.png', '*.webp'):
        for filepath in glob.glob(os.path.join(save_path, ext)):
            try:
                os.remove(filepath)
            except OSError:
                pass

def run_download(urls, codec_data, save_path, progress_hook):
    options = ydl_opts(codec_data, save_path, progress_hook)
    
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download(urls)
        rm_images(save_path)
            
    except Exception as e:
        print(f"Critical Error: {e}")