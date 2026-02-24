import json
import re

PLAYLIST_FILE = 'playlist.m3u' # Change to your filename
JSON_FILE = 'stream_data.json'

# Load the new data
with open(JSON_FILE, 'r') as f:
    stream_data = json.load(f)

# Create a lookup dictionary: channel name -> data
# Clean names slightly for better matching (lowercase, remove 'HD')
lookup = {}
for item in stream_data:
    clean_name = item['name'].lower().replace(' hd', '').strip()
    lookup[clean_name] = item

# Read the playlist
with open(PLAYLIST_FILE, 'r') as f:
    lines = f.readlines()

# Process lines to find and update channels
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)

    # Check if this is an EXTINF line (start of a channel entry)
    if line.startswith('#EXTINF:'):
        # Try to extract channel name (simplistic approach)
        # Assumes format: ... ,Channel Name
        match = re.search(r',([^,]+)$', line.strip())
        if match:
            original_name = match.group(1).strip()
            clean_name = original_name.lower().replace(' hd', '').strip()

            if clean_name in lookup:
                new_data = lookup[clean_name]
                print(f"Updating: {original_name}")

                # Skip ahead to update the next relevant lines
                # We expect: EXTINF, then KODIPROP lines, then EXTHTTP, then URL
                j = i + 1
                while j < len(lines) and not lines[j].startswith('#EXTINF:') and not lines[j].startswith('http'):
                    # Update license_key line
                    if 'inputstream.adaptive.license_key' in lines[j]:
                        new_lines[j] = f'#KODIPROP:inputstream.adaptive.license_key={new_data["drmLicense"]}\n'
                    # Update cookie line
                    elif lines[j].startswith('#EXTHTTP:'):
                        new_lines[j] = f'#EXTHTTP:{{"cookie":"{new_data["cookie"]}"}}\n'
                    j += 1
                # Move index forward to skip processed lines
                i = j - 1 # Will be incremented by loop
    i += 1

# Write the updated playlist back
with open(PLAYLIST_FILE, 'w') as f:
    f.writelines(new_lines)

print("Playlist update complete.")
