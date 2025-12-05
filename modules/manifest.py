import os
import json

MANIFEST_FILE = ".sync_manifest.json"

def load_manifest(directory):
    path = os.path.join(directory, MANIFEST_FILE)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_manifest(directory, manifest):
    path = os.path.join(directory, MANIFEST_FILE)
    with open(path, 'w') as f:
        json.dump(manifest, f, indent=4)

class ManifestUpdater:
    def __init__(self, directory, codec_data=None):
        self.directory = directory
        self.manifest = load_manifest(directory)
        self.new_entries = {}
        self.codec_data = codec_data

    def hook(self, d):
        if d['status'] == 'finished':
            # The filename here is usually the pre-converted one (e.g. .mp4 or .webm)
            full_path = d['filename']
            filename = os.path.basename(full_path)
            vid_id = d.get('info_dict', {}).get('id')
            
            if vid_id:
                final_filename = filename
                
                if self.codec_data:
                    codec = self.codec_data.get('codec')
                    if codec:
                        base, ext = os.path.splitext(filename)
                        
                        target_ext = f".{codec}"
                        
                        potential_filename = base + target_ext
                        potential_path = os.path.join(self.directory, potential_filename)
                        
                        if os.path.exists(potential_path):
                            final_filename = potential_filename
                        elif ext != target_ext:
                            final_filename = potential_filename

                self.new_entries[vid_id] = final_filename
                self.manifest[vid_id] = final_filename
                save_manifest(self.directory, self.manifest)
