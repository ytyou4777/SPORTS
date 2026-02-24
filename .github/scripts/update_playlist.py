import json
import re
import sys

PLAYLIST_FILE = "playlist.m3u"   # 👈 change to your actual filename
JSON_FILE = "stream_data.json"

def clean_channel_name(name):
    """Normalize channel name for matching (lowercase, remove ' hd')."""
    name = name.lower().strip()
    name = re.sub(r'\s+hd\b', '', name)  # remove " hd" (with word boundary)
    return name

def load_json_data():
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Build lookup dict: cleaned name -> full item
    lookup = {}
    for item in data:
        cleaned = clean_channel_name(item["name"])
        lookup[cleaned] = item
    return lookup

def update_playlist(lookup):
    with open(PLAYLIST_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    total_changed = 0

    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # Detect start of a channel entry
        if line.startswith("#EXTINF:"):
            # Extract channel name (assumes format: ... ,ChannelName)
            match = re.search(r',([^,]+)$', line.strip())
            if match:
                orig_name = match.group(1).strip()
                cleaned_name = clean_channel_name(orig_name)

                if cleaned_name in lookup:
                    channel_data = lookup[cleaned_name]
                    print(f"Updating: {orig_name}")

                    # Move forward to find and update the next relevant lines
                    j = i + 1
                    updated_in_block = False
                    while j < len(lines) and not lines[j].startswith("#EXTINF:"):
                        # Update license_key line
                        if "inputstream.adaptive.license_key" in lines[j]:
                            new_lines[j] = f'#KODIPROP:inputstream.adaptive.license_key={channel_data["drmLicense"]}\n'
                            updated_in_block = True
                        # Update cookie line
                        elif lines[j].startswith("#EXTHTTP:"):
                            new_lines[j] = f'#EXTHTTP:{{"cookie":"{channel_data["cookie"]}"}}\n'
                            updated_in_block = True
                        # Update stream URL (the line after #EXTHTTP typically)
                        elif lines[j].startswith("http"):
                            new_lines[j] = f'{channel_data["link"]}\n'
                            updated_in_block = True
                        j += 1

                    if updated_in_block:
                        total_changed += 1
                    # Advance main index to the end of this block
                    i = j - 1  # will be incremented by loop
        i += 1

    if total_changed > 0:
        with open(PLAYLIST_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"✅ Updated {total_changed} channels.")
    else:
        print("ℹ️ No channels needed updating.")

if __name__ == "__main__":
    lookup = load_json_data()
    update_playlist(lookup)
