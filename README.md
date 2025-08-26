> [!WARNING]
> **This app can modify and delete video files.**  
> Use with caution, especially when pointing to personal or irreplaceable media.  
> It is strongly recommended to test on copies of videos before using it on your main library.

## 🔧 Setup Instructions
> 1. Clone repository and navigate to root folder of project
> 2. Create python environment (python version>=3.10)
> 3. Run "pip install -e ." to install dependencies
> 4. Create/edit configuration file for backend (example in config/)
> 5. Run "python backend/vid_server.py <path_to_your_config_file>"
> 6. To access video player, in browser go to URL: <br>
>  "<your_host_ip>:<your_port>/frontend/vid_player.html"


## ⚙️ Backend Configurations
> [!IMPORTANT]
> **Ensure your customised configuration file has the exact same sections, else the program will crash.**  

> - **Server** - Backend server and network settings
>   - **HOST** - Address to host the backend
>   - **PORT** - Port for the backend to listen on
> - **Paths** - Absolute path to user resources
>   - **VIDS_PATH** - Path to the directory containing videos
>   - **DB_PATH** - Path to create/store the database file
> - **Preprocess** - Video file preprocessing settings
>   - **PLATFORM** - Platform to run on, options are (Windows/MacOS/Linux)
>   - **MODIFY** - Set if preprocessing is allowed to modify filename of videos
>   - **DELETE** - Set if preprocessing is allowed to delete videos
>   - **HIDE** - Set if preprocessing is allowed to change video visibility

## ⌨️ Hotkeys
> [!NOTE]
> This video player support keyboard shortcuts for quick control. <br>
> Hotkey rebinding and customisation will be coming soon.

| **Function** | **Key** | **Description** |
|--------------|--------|-----------------|
| Console | Backquote | Toggle webpage command console |
| Change Modify Mode | C | Change mode of Increase/Decrease keys <br> (Volume or Time Skip Amount) |
| Increase | W | Increase Volume / Increase Time Skip Amount |
| Decrease | S | Decrease Volume / Decrease Time Skip Amount |
| Skip Forward | D | Skip amount of time forward once |
| Skip Backward | A | Skip amount of time backwards once |
| Speed Up | N | Increase video playback speed |
| Speed Down | B | Decrease video playback speed |
| Toggle Volume | M | Toggle volume of video (Mute / Unmute) |
| Play/Pause | Space | Toggle playback state of video |
| Rotate | R | Rotate video display element |
| Flip | F | Reflect/flip video display element |
| Scale Up | ] | Increase scale of video display element |
| Scale Down | [ | Decrease scale of video display element |
| Next Highlight | H | Go to playback time of the next stored Highlight |
| Prev Highlight | G | Go to playback time of the previous stored Highlight |
| Highlight | 0 | Add Highlight at current playback time of video |
| Goto | 1, 2, 3, 4, 5 | Go to predifined % of video playback time |
| Display Time | T | Display current time and total time of video |
| Display Info | V | Display current volume and playback time of video |
| Display Count | I | Display the 1-index of the video and total number of videos |
| Next | E | Go to next video in list |
| Prev | Q | Go to previous video in list |
| Lock | Right Ctrl | Lock change video functions |
| Controls | U | Toggle html5 native video player control UI |
| FullScreen | X | Enter fullscreen mode <br> (browser fullscreen recommended over this) |
| Toggle Mini | P | Toggle miniplayer mode for video element |
| Toggle List | L | Toggle list overlay for faster video navigation |
| List Start/End | Slash | Toggle list to first/last page |
| List Next | Period | Go to next page of list |
| List Prev | Comma | Go to previous page of list |

## 🖥️ Console Commands
> [!NOTE]
> Some commands are destructive, use with caution

| **Command** | **Description** |
|-------------|-----------------|
| name | Return title (filename) of current video |
| highlights | Return list of integer time values for all highlights in current video |
| hl <integer> | Add highlight of given playback time |
| rmhl <integer> | Remove highlight at given playback time |
| vol <integer> | Modify default start volume of current video |
| scale | Save current video scale as default |
| rot | Save current video rotations as default |
| refl | Save current video reflections/flips as default |
| remove | **Delete** current video **after player reload** |
| goto <integer> | Go to the video with given 1-index |
| clear | Clear console outputs and history |

