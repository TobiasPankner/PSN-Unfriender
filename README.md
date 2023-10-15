# PSN Unfriender
[![GitHub stars](https://img.shields.io/github/stars/TobiasPankner/PSN-Unfriender.svg?style=social&label=Star)](https://GitHub.com/TobiasPankner/PSN-Unfriender/stargazers/)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=3TU2XDBK2JFU4&source=url)

- [Prerequisites](#prerequisites)
- [Run the script](#run-the-script)
- [Configuration options](#configuration-options)

Python script to mass delete PSN friends.

## Prerequisites
  
 - Python 3 ([Download](https://www.python.org/downloads/)) 
 - [Playstation Network](https://www.playstation.com/) Account
 
## Run the script

 :warning: **Treat the npsso token like your password!**

 1. Rename the [configuration.example.json](configuration.example.json) file to `configuration.json`
 2. Log into the [Playstation website](https://www.playstation.com/)
 3. Visit this page: https://ca.account.sony.com/api/v1/ssocookie
 4. Copy the npsso token and paste it in the `configuration.json` file
 5. Install dependencies: `pip install -r requirements.txt`
 6. Run the script `python unfriender.py`

## Configuration options

The only thing to configure is the friends you want to keep.  
To do this, a list of patterns can be specified in the `configuration.json` file.  

**Example:**  
If you want to keep all friends that have the word "Warrior" or "Wicked" somewhere in their name.  
This is case-sensitive!
```json
{
  "npsso_token": "YOUR TOKEN",
  "nameWhitelistPatterns": [
    ".*Warrior.*",
    ".*Wicked.*"
  ]
}
```
The output of the program then might look like this:
```
Found 12 friends

Friends to remove (9): 
FierceChampion42
MightyDragon99
RadiantPhoenix48
DaringSorcerer64
DaringTitan45
MysticNinja42
VividLegend82
DaringPhoenix41
VividSamurai69

Friends to keep (3): 
WickedNinja30
WickedDragon84
FierceWarrior92
```



