import re
import os
import random
import sys
from datetime import datetime, timezone

import bs4
import requests

if len(sys.argv) != 2:
    print(f"Error: This program needs 1 argument, got {len(sys.argv) - 1}\n")
    print(f"Usage: {sys.argv[0]} <file-to-write-to>\n")
    print("Parses all MCPE releases from Modscraft and writes to specified Markdown file.")
    sys.exit(1)

def pathify(string):
    return re.sub(r'[^a-z0-9_.-]', '', string.replace(' ', '_').lower())

def create_md_table(data, width):
    table = f"{'| ' * width}|\n{'|-' * width}|\n"
    for i in range(0, len(data), width):
        table += "| " + " | ".join(data[i:i + width]) + " |\n"
    return table

user_agents = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/10.3 Mobile/14G60 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_5 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/9.3 Mobile/13G36 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_4 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/8.4 Mobile/12H143 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/7.1 Mobile/11D257 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_6 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.1 Mobile/10B500 Safari/536.26",
    "Mozilla/5.0 (Linux; Android 14; SM-S916B Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G996B Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/112.0.5615.121 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S908U Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.5845.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A536U1 Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.171 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G998U Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/112.0.5615.121 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S911B Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.5845.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G781B Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.171 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-A716U Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/112.0.5615.121 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G973F Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.171 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S901U1 Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.5845.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A536E Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.171 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G998W Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/112.0.5615.121 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S906U Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.5845.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A336E Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.171 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G996U1 Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/112.0.5615.121 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S908W Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.5845.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G981B Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.171 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-A716B Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/112.0.5615.121 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A426B Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.171 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S918U1 Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.5845.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991U1 Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.171 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G970U Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/112.0.5615.121 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S901E Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.5845.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A526B Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.171 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G986U Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/112.0.5615.121 Mobile Safari/537.36"
]
user_agent = random.choice(user_agents)
print(f"* Parser has started")
print(f"= User agent for today is \"{user_agent}\"")
markdown_output = f"- :open_file_folder: Source available at [**ModsCraft.Net**](https://modscraft.net/en/mcpe/)"
markdown_output += f"\n- :clock2: Updated **every 12 hours** at `00:00 UTC` and `12:00 UTC`"
markdown_output += f"\n- :rocket: **Last update:** `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC`\n"
print("* Creating directory 'version'")
writedir = os.path.dirname(sys.argv[1])
os.makedirs(os.path.join(writedir, "version"), exist_ok=True)
print("* Getting releases")
resp = requests.get("https://modscraft.net/en/mcpe/", headers={"User-Agent": user_agent})
if not resp.ok:
    print(f"! ModsCraft returned {resp.status_code}")
    sys.exit(1)
soup = bs4.BeautifulSoup(resp.text, "html.parser")
releases = {i.text: i["href"] for i in soup.find("div", class_="versions-history").find_all("a")}
version_links = []
for title, release in releases.items():
    print(f"\n= Starting work on version {title}")
    ver = requests.get(release, headers={"User-Agent": user_agent})
    if not ver.ok:
        print(f"! ModsCraft returned {resp.status_code}")
        sys.exit(1)
    rel_soup = bs4.BeautifulSoup(ver.text, "html.parser")
    version_output = f"## Minecraft {title} APKs\n"
    version_output += "| Download | Size |\n"
    version_output += "|----------|------|\n"
    for download in rel_soup.find_all("a", class_="download-item"):
        print("* Adding file ", end='')
        down_req = requests.get(download["href"], headers={"User-Agent": user_agent})
        if not down_req.ok:
            print(f"! ModsCraft returned {resp.status_code}")
            sys.exit(1)
        apk = bs4.BeautifulSoup(down_req.text, "html.parser")
        download_id = re.search(r'id=(\d+)', download["href"]).group(1)
        down_spans = download.find_all("span")
        file_name = apk.find("p").text
        print(file_name)
        size = down_spans[2].text[1:-1]
        download_link = f"https://modscraft.net/en/downloads/{download_id}"
        version_output += f"| [:package: `{file_name}`]({download_link}) | :floppy_disk: {size} \n"
    print(f"= Finished work on version {title}")
    filename = f"mc{pathify(title)}.md"
    try:
        with open(os.path.join(writedir, "version", filename), "w") as f:
            f.write(version_output)
    except PermissionError:
        print("! Unable to access file, not enough permissions")
        sys.exit(1)
    except IOError as e:
        print(f"! I/O error while writing to file: {e}")
        sys.exit(1)
    print("= Adding to main file")
    version_links.append(f"**[:package: Minecraft {title}](version/{filename})**")
markdown_output += f"\n{create_md_table(version_links, 3)}"

print("\n= All done, writing to file")
try:
    with open(os.path.join(sys.argv[1]), "w") as f:
        f.write(markdown_output)
except PermissionError:
    print("! Unable to access file, not enough permissions")
    sys.exit(1)
except IOError as e:
    print(f"! I/O error while writing to file: {e}")
    sys.exit(1)
print(f"* Wrote to '{sys.argv[1]}' successfully")
