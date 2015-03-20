NCutil
======

Notification Center command line utility - ***Add and remove apps, set alert styles.***
OS Mavericks and [Yosemite](https://github.com/jasonpjohnson/NCutil/commit/3028e8baccc646b60712fa0cc08de2be52b4e11b)

# Short Demo Video
<a href="http://www.youtube.com/watch?feature=player_embedded&v=4Mo6FYXGQOo
" target="_blank"><img src="http://img.youtube.com/vi/4Mo6FYXGQOo/0.jpg" 
alt="Modify Notification Center from the command line in OS X" width="240" height="180" border="10" /></a>

# Examples
## Add and remove apps from Notification Center
Adding and removing apps is perfect for deploying software silently or having it pre-configured so the user doesn't have to do anything.

### Add apps

- ```NCutil.py -i com.apple.com.noodlesoft.HazelHelper```
- ```NCutil.py --insert com.apple.com.noodlesoft.HazelHelper```

### Remove apps

- ```NCutil.py -r com.apple.com.barebones.textwrangler```
- ```NCutil.py --remove com.apple.com.barebones.textwrangler```

## Adjust Alert Duration (Alerts or Banners)
Yosemite also added the option for *None*.

- ```NCutil.py -a com.apple.Safari alert```
- ```NCutil.py -a com.apple.reminders banner```
- ```NCutil.py -a com.apple.appstore none```

## Suppress Apple Update Notifications
Apple has a lot of different apps that show notifications, which do not show up in the GUI.  Examples are battery notices, Bluetooth, updates, keychain, etc.  You can suppress these hidden notifications with a few simple commands:

- ```NCutil.py --alerts com.apple.maspushagent none```
- ```NCutil.py -a _SYSTEM_CENTER_:com.apple.storeagent none```
- ```NCutil.py -a _SYSTEM_CENTER_:com.apple.noticeboard none```
 
You can also try removing them, but Apple seems to add them back in somehow when you reboot.
