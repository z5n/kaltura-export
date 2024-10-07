a really fast and shitty solution to download kaltura videos from an iframe on canvas. needs a lot of optimization, but it works as a rough draft.

1. pip install -r requirements.txt
2. navigate to canvas, get to your video and right click on the play button, open the link in a new tab
3. grab that link in the address bar, pass it into urls in main.py
4. python3 main.py