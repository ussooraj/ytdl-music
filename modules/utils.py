import os
import glob

def rm_images(save_path):
    """Removes all .jpg, .png, and .webp files from the directory."""
    for ext in ('*.jpg', '*.png', '*.webp'):
        for filepath in glob.glob(os.path.join(save_path, ext)):
            try:
                os.remove(filepath)
            except OSError:
                pass
