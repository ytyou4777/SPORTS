const axios = require('axios');
const fs = require('fs');

const SOURCE_URL = 'https://raw.githubusercontent.com/cloudplay97/m3u/main/jiotv-mb.m3u';
const OUTPUT_FILE = 'JIO.m3u';

async function processM3U() {
  try {
    console.log(`📥 Fetching from ${SOURCE_URL}...`);
    const response = await axios.get(SOURCE_URL, {
      timeout: 30000,
      headers: { 'User-Agent': 'Mozilla/5.0' }
    });

    const lines = response.data.split('\n');
    const outputLines = [];
    let headerProcessed = false;

    for (let line of lines) {
      line = line.trim();

      // Keep empty lines as they are (for readability)
      if (line === '') {
        outputLines.push('');
        continue;
      }

      // Ensure #EXTM3U is only once at the top
      if (line.startsWith('#EXTM3U')) {
        if (!headerProcessed) {
          outputLines.push('#EXTM3U');
          headerProcessed = true;
        }
        continue;
      }

      // Process #EXTINF lines
      if (line.startsWith('#EXTINF:')) {
        // Extract the part after the comma (channel name) if needed, but we mainly want the group-title
        // Regex to find group-title="..." and replace it
        const modifiedLine = line.replace(/group-title="([^"]*)"/, (match, group) => {
          // Prepend "Clarity TV | " to the existing group name
          return `group-title="Clarity TV | JIOTV+ | ${group}"`;
        });
        outputLines.push(modifiedLine);
      } else {
        // All other lines (URLs, #EXTHTTP, comments) stay as they are
        outputLines.push(line);
      }
    }

    fs.writeFileSync(OUTPUT_FILE, outputLines.join('\n'), 'utf8');
    console.log(`✅ Successfully written to ${OUTPUT_FILE} with modified group titles.`);
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

processM3U();
