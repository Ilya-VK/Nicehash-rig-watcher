# Minimalistic console monitor for Nicehash
Using Nicehash API.
## Requirements
Python and python `requests` package.
## Configuration
1. Create API key in [Nicehash account settings](https://www.nicehash.com/my/settings/keys) with access to:
   * Wallet Permissions / View balances, wallet activities and deposit addresses
   * Mining Permissions / View mining data and statistics

   **Save API key and secret at the very first time Nicehash show them - you won't be able to see the secret later**

<p align="center">
  <img src="https://github.com/Ilya-VK/Nicehash-rig-watcher/blob/f7490c8d4a836cb722106d11ea55cdfbe7747047/api%20settings.png" alt="API settings image" width="420"/>
</p>

2. Download `watcher.py` and `config.ini.example`.
3. Fill API credentials into `config.ini.example`, rename the file to `config.ini`.
## Usage
 Run `watcher.py`. Watch. Close or `Ctrl-C` when not needed anymore.
