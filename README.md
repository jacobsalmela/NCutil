NCutil
======

Notification Center command line utility - ***Add and remove apps, set alert styles.***
OS Mavericks and [Yosemite](https://github.com/jasonpjohnson/NCutil/commit/3028e8baccc646b60712fa0cc08de2be52b4e11b).  View changes via the GUI in real-time.

# Short Demo Video
<a href="http://www.youtube.com/watch?feature=player_embedded&v=4Mo6FYXGQOo
" target="_blank"><img src="http://img.youtube.com/vi/4Mo6FYXGQOo/0.jpg" 
alt="Modify Notification Center from the command line in OS X" width="240" height="180" border="10" /></a>

# Examples
## Add and remove apps from Notification Center
Adding and removing apps is perfect for deploying software silently or having it pre-configured so the user doesn't have to do anything.

### Add apps

- ```NCutil.py -i com.noodlesoft.HazelHelper```
- ```NCutil.py --insert com.noodlesoft.HazelHelper```

### Remove apps

- ```NCutil.py -r com.barebones.textwrangler```
- ```NCutil.py --remove com.barebones.textwrangler```

## Adjust Alert Duration (Alerts, Banners, or None)

- ```NCutil.py -a com.apple.Safari alerts```
- ```NCutil.py -a com.apple.reminders banners```
- ```NCutil.py --alert-style com.apple.appstore none```

# Multiple Bundle IDs

For `--insert`, `--remove`, and `--alert-style`, you can add multiple bundle IDs to modify the same setting for multiple apps.

- ```NCutil.py --remove com.noodlesoft.HazelHelper com.apple.Safari com.apple.reminders```

## Get Current Alert Setting
You can find out what the app's current alert setting is with the `-g` flag or `--get-alert-style`.

- ```NCutil.py -g com.teamviewer.TeamViewer```
- ```NCutil.py --get-alert-style com.teamviewer.TeamViewer```

which will return something like this:

```com.teamviewer.TeamViewer has notification style: banners```

## Suppress Apple Update Notifications
Apple has a lot of different apps that show notifications, which do not show up in the GUI.  Examples are battery notices, Bluetooth, updates, keychain, etc.  You can suppress these hidden notifications with a few simple commands.  I use the following to disable the App Store and Software Update notifications.

- ```NCutil.py --alerts com.apple.maspushagent none```
- ```NCutil.py -a _SYSTEM_CENTER_:com.apple.storeagent none```
- ```NCutil.py -a _SYSTEM_CENTER_:com.apple.noticeboard none```
 
You can remove **all** of these hidden Notification sources by using the `-remove-system-center` option but is not fully-supported as we don't know what each of them do.  If you decide to try it, this is the equivalent to setting each one individually to an alert style of `none`.

- ```NCutil.py --remove-system-center```

### Remove `_SYSTEM_CENTER_` At Your Own Risk 

To add a little more detail to the command above, the `_SYSTEM_CENTER_` entries are hidden from the GUI.  Apple is obviously not expecting users to change any of those preferences (since there is no UI to do so) and so it would be prudent to not modify those.  However, this utility lets you do that.  You can do so *at your own risk*.  Personally, I have had them turned off for a few weeks now without issue, but that doesn't mean it won't break later.

Additionally, if there were some sources you still wanted to have, you can simply re-enable them on an individual basis.

- ```NCutil.py -a _SYSTEM_CENTER_:com.apple.storeagent banners```
- ```NCutil.py -a _SYSTEM_CENTER_:com.apple.battery-monitor banners```

# Changelog

**2.1**

- `--get-alert-style` allows you to see what alert style the app currently is set to
- `--remove-system-center` removes all hidden notification, but do so at your own risk
- allow multiple arguments for `--insert`, `--remove`, and `--alert-style`
- syntax changed to `--alert-style` from `--alertstyle` for easier readability
- find the most recently used .db if multiple ones exist

**2.0**

- Yosemite Support

**1.0**

- Initial release. Mavericks support.