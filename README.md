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

- ```NCutil.py -a com.apple.Safari alerts```
- ```NCutil.py -a com.apple.reminders banners```
- ```NCutil.py -a com.apple.appstore none```

## Get Current Alert Setting
You can find out what the app's current alert setting is with the `-g` flag.

- ```NCutil.py -g com.teamviewer.TeamViewer```
- ```NCutil.py --getalertstyle com.teamviewer.TeamViewer```

which will return something like this:

```com.teamviewer.TeamViewer has notification style: banners```

## Suppress Apple Update Notifications
Apple has a lot of different apps that show notifications, which do not show up in the GUI.  Examples are battery notices, Bluetooth, updates, keychain, etc.  You can suppress these hidden notifications with a few simple commands.  I use the following to disable the App Store and Software Update notifications.

- ```NCutil.py --alerts com.apple.maspushagent none```
- ```NCutil.py -a _SYSTEM_CENTER_:com.apple.storeagent none```
- ```NCutil.py -a _SYSTEM_CENTER_:com.apple.noticeboard none```
 
You can remove **all** of these hidden Notification sources by using the `-s` or `-remove-system-center` options.  This is the equivalent to setting each one individually to an alert style of `none`.

- ```NCutil.py -s```
- ```NCutil.py -remove-system-center```

If there were some sources you still wanted to have, you can simply re-enable them.

- ```NCutil.py -a _SYSTEM_CENTER_:com.apple.storeagent banners```
- ```NCutil.py -a _SYSTEM_CENTER_:com.apple.battery-monitor banners```

Apple hides these from the GUI, so this utility kind of works around that, so you can modify them at your own risk.

