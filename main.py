from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import m3u8
import os
import requests
import subprocess
import time

urls = [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
]

def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

def clear_m3u8_files():
    directory = ""
    for file in os.listdir(directory):
        if file.endswith('.m3u8'):
            os.remove(os.path.join(directory, file))
    print("Cleared existing .m3u8 files from directory")

def get_index_url(url):
    clear_m3u8_files()
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)

    play_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.icon-play.comp.largePlayBtn"))
    )
    play_button.click()

    js_script = """
    (function() {
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            const url = args[0];
            
            if (typeof url === 'string' && url.startsWith("https://cfvod.kaltura.com/") && url.includes("index.m3u8")) {
                window.location.href = url;
                return;
            }
            
            return originalFetch.apply(this, args);
        };

        const originalXHR = window.XMLHttpRequest.prototype.open;
        window.XMLHttpRequest.prototype.open = function(method, url, ...args) {
            if (url.startsWith("https://cfvod.kaltura.com/") && url.includes("index.m3u8")) {
                // navigate to the url, which downloads the index file
                window.location.href = url;
                return;
            }
            return originalXHR.apply(this, [method, url, ...args]);
        };
    })();
    """

    driver.execute_script(js_script)
    print("JavaScript injected, waiting for index.m3u8 file...")
    time.sleep(3)
    driver.quit()

    directory = "/Users/josh/Downloads"
    for file in os.listdir(directory):
        if file.endswith('index.m3u8'):
            downloaded_file = os.path.join(directory, file)
            print(f"Downloaded index.m3u8 to {downloaded_file}")
            return downloaded_file

    raise FileNotFoundError("index.m3u8 was not downloaded to the Downloads directory")

def main(url, output_filename):
    index_file = get_index_url(url)
    print(f"Using index.m3u8 file: {index_file}")

    with open(index_file, 'r') as f:
        index_content = f.read()

    playlist = m3u8.loads(index_content)

    os.makedirs("ts_files", exist_ok=True)

    for i, segment in enumerate(playlist.segments):
        ts_url = segment.uri
        ts_filename = f"ts_files/segment_{i:03d}.ts"
        print(f"Downloading {ts_url} to {ts_filename}")
        download_file(ts_url, ts_filename)

    with open("file_list.txt", "w") as f:
        for i in range(len(playlist.segments)):
            f.write(f"file 'ts_files/segment_{i:03d}.ts'\n")

    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", "file_list.txt", "-c", "copy", output_filename])

    os.remove("file_list.txt")
    for file in os.listdir("ts_files"):
        os.remove(os.path.join("ts_files", file))
    os.rmdir("ts_files")

    print(f"Conversion complete. Output file: {output_filename}")

if __name__ == "__main__":
    for i, url in enumerate(urls):
        output_filename = f"output_{i+1}.mp4"
        print(f"Processing URL {i+1}/{len(urls)}")
        main(url, output_filename)
        print(f"Finished processing URL {i+1}/{len(urls)}")
        print("---")
    
    print("All URLs processed successfully.")