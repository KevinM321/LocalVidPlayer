## ⚠️ Warning
> **🚨 IMPORTANT: This app can modify and delete video files.**  
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


## ⚙️ BackEnd Configurations
> **🚨 IMPORTANT: Ensure your customised configuration file has the exact same sections, else the
> program will crash.**  
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
