# Minimalistic console monitor for Nicehash
Using Nicehash API.
## Requirements
Python and python `requests` package.
## Configuration
1. Create API key in [Nicehash account settings](https://www.nicehash.com/my/settings/keys) with access to:
   * Wallet Permissions / View balances, wallet activities and deposit addresses
   * Mining Permissions / View mining data and statistics

<img src="https://github.com/Ilya-VK/Nicehash-rig-watcher/blob/f7490c8d4a836cb722106d11ea55cdfbe7747047/api%20settings.png" alt="API settings image" width="420" align="middle"/>

2. Download `watcher.py` and `api.config.example`.
3. Fill API credentials into `api.config.example`, rename the file to `api.config`.
## Usage
 Run `watcher.py`. Watch. Close or `Ctrl-C` when not needed anymore.
