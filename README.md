NCutil
======

Notification Center command line utility - Add and remove apps, set alert styles

Currently works on Mavericks only.  Yosemite changed a lot about Notification Center, so the simple .db file is no longer used.

## Suppress Apple Update Notifications In Mavericks
You can suppress these notifications with a few simple commands:

`NCutil.py --remove com.apple.maspushagent`

`NCutil.py --remove _SYSTEM_CENTER_:com.apple.storeagent`

![Ready to install](http://i.imgur.com/IMQnWqw.png)

![Try again](http://i.imgur.com/tvDib3B.png)

![Not installed](http://i.imgur.com/sOwy0de.png)

# Yosemite Support
`com.apple.notificationcenterui.plist` seems to be where most of the settings are stored now.  The plugins or widgets are in the Containers folder.  Getting around the sandbox will be difficult but I am still trying to find a way to get this utility to work in Yosemite.
