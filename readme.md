# Minimalistic console monitor for Nicehash
Using Nicehash API.
## Requirements
Python and python `requests` package. Tested only on Windows with Python 3.9 currently.
## Configuration
1. **Important**: save API key and secret at the very first time Nicehash show them.<br>Create API key in [Nicehash account settings](https://www.nicehash.com/my/settings/keys) with access to:
   * Wallet Permissions / View balances, wallet activities and deposit addresses
   * Mining Permissions / View mining data and statistics

<p align="center">
  <img src="https://github.com/Ilya-VK/Nicehash-rig-watcher/blob/f7490c8d4a836cb722106d11ea55cdfbe7747047/api%20settings.png" alt="API settings image" width="420"/>
</p>

2. Download `watcher_console.py` or `watcher_gui.py` and `config.ini.example`.
3. Fill API credentials into `config.ini.example`, rename the file to `config.ini`.
## Usage
 On Windows run `watcher_console.py` or `pythonw watcher_gui.py`. Watch. Close when not needed anymore.
