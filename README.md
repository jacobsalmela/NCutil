NCutil
======

Notification Center command line utility - ***Add and remove apps, set alert styles.***
OS Mavericks and [Yosemite](https://github.com/jasonpjohnson/NCutil/commit/3028e8baccc646b60712fa0cc08de2be52b4e11b).  View changes via the GUI in **real-time**.

# Short Demo Video
<a href="http://www.youtube.com/watch?feature=player_embedded&v=4mPsqD30eCY
" target="_blank"><img src="http://img.youtube.com/vi/4mPsqD30eCY/0.jpg"
alt="Modify Notification Center from the command line in OS X" width="600" height="400" border="0" /></a>


# Add and remove apps from Notification Center
Adding and removing apps is perfect for deploying software silently or having it pre-configured so the user doesn't have to do anything.

## Add apps

- ```NCutil.py -i com.noodlesoft.HazelHelper```
- ```NCutil.py --insert com.noodlesoft.HazelHelper```

## Remove apps

- ```NCutil.py -r com.barebones.textwrangler```
- ```NCutil.py --remove com.barebones.textwrangler```

# Get Current Settings
Running a command like this:

- ```NCutil.py --get-info com.apple.reminders```

will return something like this:

```
Notification Center settings for Reminders.app:
    Reminders.app alert style:         Alerts
    Show notifications on lock screen: Yes
    Show message preview:              Always
    Show in Notification Center:       5 Recent Items
    Badge app icon:                    Yes
    Play sound for notifications:      Yes
```

## Get Individual Settings

### Get The Current Alert Settings

You can find out what the app's current alert setting is with the `-g` flag or `--get-alert-style`.

- ```NCutil.py -g com.teamviewer.TeamViewer```
- ```NCutil.py --get-alert-style com.teamviewer.TeamViewer```

which will return a one line response: `none`, `banners`, or `alerts`

### Get Other Settings

You can check if individual settings are on or off using some of the examples shown below, which will return a one line response.

`NCutil.py --get-show-on-lock-screen com.apple.iCal`

returns `true` or `false`

`NCutil.py --get-badge-app-icon com.apple.iCal`

returns `true` or `false`

`NCutil.py --get-sound com.apple.iCal`

returns `true` or `false`

`NCutil.py --get-show-in-notification-center com.apple.iCal`

returns a number: `0`, `5`, `10`, or `20`

# Change Settings

## Adjust Alert Duration (Alerts, Banners, or None)

- ```NCutil.py -a alerts com.apple.Safari```
- ```NCutil.py -a banners com.apple.reminders```
- ```NCutil.py --alert-style none com.apple.appstore```

## Adjust Other Checkbox Settings

You can adjust any of the checkboxes in the GUI such as the badge icon, number of recent items, whether or not to show it on the lock screen, etc.
![Notifications that can be adjusted with NCutil.py](http://i.imgur.com/q0aRdGl.png)

Don't show iCal Notifications on the lock screen

- ```NCutil.py --show-on-lock-screen true com.apple.iCal```

Disable the badge app icon for Message

- ```NCutil.py --badge-app-icon false com.apple.iChat```

Disable the sound for TextWrangler

- ```NCutil.py --sound false com.barebones.textwrangler```

Set the amount of recent Notifications to show to 20 for Dropbox

- ```NCutil.py --show-in-notification-center 20 com.getdropbox.dropbox```

# Multiple Bundle IDs

Most of the options like `--insert`, `--remove`, or `--alert-style`, allow you to add multiple bundle IDs to modify the same setting for multiple apps.

- ```NCutil.py --remove com.noodlesoft.HazelHelper com.apple.Safari com.apple.reminders```

# `_SYSTEM_CENTER_` Notifications

Apple has a lot of different apps that show notifications, which do not show up in the GUI. You can remove **all** of these hidden Notification sources by using the `-remove-system-center` option but is not fully-supported as we don't know what they all do.  If you decide to try it, this is the equivalent to setting each one individually to an alert style of `none`.

- ```NCutil.py --remove-system-center```

## Remove `_SYSTEM_CENTER_` At Your Own Risk

To add a little more detail to the command above, the `_SYSTEM_CENTER_` entries are hidden from the GUI.  Apple is obviously not expecting users to change any of those preferences (since there is no UI to do so) and so it would be prudent to not modify those.  However, this utility lets you do that.  You can do so *at your own risk*.  Personally, I have had them turned off for a few weeks now without issue, but that doesn't mean it won't break later.

Additionally, if there were some sources you still wanted to have notification for, you can simply re-enable them on an individual basis.

- ```NCutil.py -a banners _SYSTEM_CENTER_:com.apple.storeagent```
- ```NCutil.py -a banners _SYSTEM_CENTER_:com.apple.battery-monitor```

### Suppress Apple Update Notifications Like The "Free Yosemite Upgrade"
From what I can tell, these are the items you need to disable to [stop the Yosemite upgrade Notification](http://jacobsalmela.com/hide-free-yosemite-upgrade-notification-with-ncutil-py/).  

![Hide the Free Yosemite Upgrade notification](http://i.imgur.com/Vw4VlJM.png)

- ```NCutil.py -a none _SYSTEM_CENTER_:com.apple.storeagent```
- ```NCutil.py -a none _SYSTEM_CENTER_:com.apple.noticeboard```

Disabling the App Store Notifications may also help:

- ```NCutil.py --alerts none com.apple.maspushagent```

# Known Issues

If Do Not Disturb is **on** and you run a command that modifies a setting, Do Not Disturb will be **turned off** unintentionally.  This seems to **only happen in Mavericks** and is likely caused by the `killall NotificiationCenter`, which is what allows the commands to show up in real time.

![Do Not Disturb bug](http://i.imgur.com/SgeeTcA.png)

# Changelog

**2.4**

- added support for OS X (10.11) El Capitan

**2.3**

- added `--get-show-on-lock-screen`
- added `--get-badge-app-icon`
- added `--get-sound`
- added `--get-show-in-notification-center`
- reformatted help menu into groups of similar settings

**2.2**

- `--get-info` allows you to see what all the current settings are
- `--show-on-lock-screen` can now be set to `true` or `false`
- `--badge-app-icon` can now be set to `true` or `false`
- `--sound` can now be set to `true` or `false`
- `--show-in-notification-center` can now be set to `0`, `5`, `10` or `20`
- improved help menu
- reduced verbosity of `--get-alert-style` since more information can be found with `--get-info`


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
