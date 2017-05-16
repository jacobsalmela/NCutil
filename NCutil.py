#!/usr/bin/python
# NCutil is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
##############################
######### IMPORTS ############
import sys
import argparse
import os
import subprocess
import sqlite3

from platform import mac_ver
from glob import glob

# even though this is not ideal Python form, we're moving these
# imports into the functions that need them since these are slow
# to import
#from Foundation import NSBundle, NSFileManager
#from AppKit import NSWorkspace

##############################
######## FUNCTIONS ###########
def usage():
    return """
(c) 2015 by Jacob Salmela.  http://jacobsalmela.com
Modify OS X's Notification Center from the command line
"""


def get_osx_major():
    '''Return OS X version in format of 10.x.x'''
    v, _, _ = mac_ver()
    #Parse Out Major Version, mac_ver() can produce 10.10.2, 10.9.5, 10.8..
    return v.split('.')[0] + "." + v.split('.')[1]


def get_nc_db():
    '''Returns a path to the current (hopefully?) NotificationCenter db'''
    nc_db = None
    osx_major = get_osx_major()
    if osx_major == '10.8' or osx_major == '10.9':
        nc_nb_path = os.path.expanduser(
            '~/Library/Application Support/NotificationCenter/')
        nc_dbs = glob(nc_nb_path + '*.db')
        if nc_dbs:
            nc_dbs.sort(key=os.path.getmtime)
            # most recently modified will be the last one
            nc_db = nc_dbs[-1]
    # Support for osx 10.10 added via randomly generated id for
    # Notification Center Database
    elif osx_major == '10.10' or osx_major == '10.11' or osx_major == '10.12':
        darwin_user_dir = subprocess.check_output(
            ['/usr/bin/getconf', 'DARWIN_USER_DIR']).rstrip()
        nc_db = os.path.join(
            darwin_user_dir, 'com.apple.notificationcenter/db/db')
    return nc_db


def connect_to_db():
    '''Connect to the Notification Center db and return connection object
    and cursor'''
    conn = None
    curs = None
    #Connect To SQLLite
    nc_db = get_nc_db()
    if nc_db:
        conn = sqlite3.connect(nc_db)
        conn.text_factory = str
        curs = conn.cursor()
    return conn, curs


def kill_notification_center():
    '''Send a kill signal to NotificationCenter and usernoted; they will
    relaunch'''
    subprocess.call(['/usr/bin/killall', 'NotificationCenter'])
    subprocess.call(['/usr/bin/killall', 'usernoted'])


def commit_changes(conn):
    '''Apply the changes and close the sqlite connection'''
    conn.commit()
    conn.close()


def verboseOutput(*args):
    #------------------------
    if verbose:
        try:
            print "Verbose:", args
        except:
            pass


def list_clients():
    '''List all bundleids in database'''
    conn, curs = connect_to_db()
    curs.execute("select bundleid from app_info")
    for row in curs.fetchall():
        print row[0]
    conn.close()


def get_available_id(curs):
    '''Get the highest app_id, then increment'''
    curs.execute("select app_id from app_info")
    # return first field of last row
    last_id = curs.fetchall()[-1][0]
    return last_id + 1


def insert_app(bundle_ids):
    '''Adds bundle_ids to Notification Center database'''
    conn, curs = connect_to_db()
    for bundle_id in bundle_ids:
        if not bundleid_exists(bundle_id):
            next_id = get_available_id(curs)
            curs.execute("INSERT INTO app_info VALUES('%s', '%s', '14', '5', '%s')"
                         % (next_id, bundle_id, next_id))
        else:
            print >> sys.stderr, "%s is already in Notification Center" % bundle_id

    commit_changes(conn)
    kill_notification_center()


def remove_app(bundle_ids):
    '''Removes bundle_ids from Notification Center database'''
    conn, curs = connect_to_db()
    for bundle_id in bundle_ids:
        if not bundleid_exists(bundle_id):
            print >> sys.stderr, (
                "WARNING: %s not in Notification Center" % bundle_id)
        else:
            curs.execute("DELETE from app_info where bundleid IS '%s'" % (bundle_id))

    commit_changes(conn)
    kill_notification_center()


def set_flags(flags, bundle_id):
    '''Sets Notification Center flags for bundle_id'''
    conn, curs = connect_to_db()
    curs.execute("UPDATE app_info SET flags='%s' where bundleid='%s'"
                  % (flags, bundle_id))
    commit_changes(conn)


def bundleid_exists(bundle_id):
    '''Returns a boolean telling us if the bundle_id is in the database.'''
    conn, curs = connect_to_db()
    curs.execute("SELECT bundleid from app_info WHERE bundleid IS '%s'"
                 % bundle_id)
    matching_ids = [row[0] for row in curs.fetchall()]
    conn.close()
    return len(matching_ids) > 0


def get_matching_ids(match_string):
    '''Returns any bundle_ids matching the match_string'''
    conn, curs = connect_to_db()
    curs.execute("SELECT bundleid from app_info WHERE bundleid LIKE '%s'"
                 % match_string)
    matching_ids = [row[0] for row in curs.fetchall()]
    conn.close()
    return matching_ids


def get_flags(bundle_id):
    '''Returns flags for bundle_id'''
    conn, curs = connect_to_db()
    curs.execute("SELECT flags from app_info where bundleid='%s'" % (bundle_id))
    try:
        flags = curs.fetchall()[0][0]
    except IndexError:
        flags = 0
    conn.close()
    return int(flags)


def get_show_count(bundle_id):
    '''Returns number of items to show in Notification Center for bundle_id'''
    conn, curs = connect_to_db()
    curs.execute("SELECT show_count from app_info where bundleid='%s'" % (bundle_id))
    try:
        flags = curs.fetchall()[0][0]
    except IndexError:
        flags = 0
    conn.close()
    return int(flags)


def remove_system_center():
    '''Sets alert style to 'none'' for all bundle_ids starting with
    _SYSTEM_CENTER_:. Not convinced this is a great idea, but there it is...'''
    set_alert('none', get_matching_ids('_SYSTEM_CENTER_:%'))


def get_app_name(bundle_id):
    '''Get display name for app specified by bundle_id'''
    from AppKit import NSWorkspace
    from Foundation import NSFileManager
    app_path = NSWorkspace.sharedWorkspace(
        ).absolutePathForAppBundleWithIdentifier_(bundle_id)
    if app_path:
        return NSFileManager.defaultManager().displayNameAtPath_(app_path)
    return bundle_id


def get_bundle_id(app_name):
    '''Given an app_name, get the bundle_id'''
    from AppKit import NSWorkspace
    from Foundation import NSBundle
    app_path = NSWorkspace.sharedWorkspace(
        ).fullPathForApplication_(app_name)
    if app_path:
        return NSBundle.bundleWithPath_(app_path).bundleIdentifier()
    return None


# flags are bits in a 16 bit(?) data structure
DONT_SHOW_IN_CENTER = 1 << 0
BADGE_ICONS = 1 << 1
SOUNDS = 1 << 2
BANNER_STYLE = 1 << 3
ALERT_STYLE = 1 << 4
UNKNOWN_5 = 1 << 5
UNKNOWN_6 = 1 << 6
UNKNOWN_7 = 1 << 7
UNKNOWN_8 = 1 << 8
UNKNOWN_9 = 1 << 9
UNKNOWN_10 = 1 << 10
UNKNOWN_11 = 1 << 11
SUPPRESS_NOTIFICATIONS_ON_LOCKSCREEN = 1 << 12
SHOW_PREVIEWS_ALWAYS = 1 << 13
SUPPRESS_MESSAGE_PREVIEWS = 1 << 14
UNKNOWN_15 = 1 << 15


def error_and_exit_if_not_bundle_exists(bundle_id):
    '''Print an error and exit if bundle_id doesn't exist.'''
    if not bundleid_exists(bundle_id):
        print >> sys.stderr, "%s not in Notification Center" % bundle_id
        exit(1)


def get_alert_style(bundle_id):
    '''Print the alert style for bundle_id'''
    error_and_exit_if_not_bundle_exists(bundle_id)
    current_flags = get_flags(bundle_id)
    if current_flags & ALERT_STYLE:
        print "alerts"
    elif current_flags & BANNER_STYLE:
        print "banners"
    else:
        print "none"


def get_show_on_lock_screen(bundle_id):
    '''Print state of "Show notifications on lock screen"'''
    error_and_exit_if_not_bundle_exists(bundle_id)
    current_flags = get_flags(bundle_id)
    if current_flags & SUPPRESS_NOTIFICATIONS_ON_LOCKSCREEN:
        print 'false'
    else:
        print 'true'


def get_badge_app_icon(bundle_id):
    '''Print state of "Badge app icon"'''
    error_and_exit_if_not_bundle_exists(bundle_id)
    current_flags = get_flags(bundle_id)
    if current_flags & BADGE_ICONS:
        print 'true'
    else:
        print 'false'


def get_notification_sound(bundle_id):
    '''Print state of "Play sound for notifications"'''
    error_and_exit_if_not_bundle_exists(bundle_id)
    current_flags = get_flags(bundle_id)
    if current_flags & SOUNDS:
        print 'true'
    else:
        print 'false'


def get_show_in_notification_center(bundle_id):
    '''Print state of "Show in Notification Center"'''
    error_and_exit_if_not_bundle_exists(bundle_id)
    current_flags = get_flags(bundle_id)
    if current_flags & DONT_SHOW_IN_CENTER:
        print 'false'
    else:
        show_count = get_show_count(bundle_id)
        if show_count == 1:
            items = '1 recent item'
        else:
            items = '%s recent items' % show_count
        print items


def get_info(bundle_id):
    '''Print the Notification Center settings for bundle_id'''
    error_and_exit_if_not_bundle_exists(bundle_id)
    current_flags = get_flags(bundle_id)
    if current_flags & ALERT_STYLE:
        style = "Alerts"
    elif current_flags & BANNER_STYLE:
        style = "Banners"
    else:
        style = "None"
    app_name = get_app_name(bundle_id)
    print "Notification Center settings for %s:" % app_name
    print '    %-34s %s' % (app_name + ' alert style:', style)
    if current_flags & SUPPRESS_NOTIFICATIONS_ON_LOCKSCREEN:
        show_notifications_on_lock_screen = False
        print "    Show notifications on lock screen: No"
    else:
        show_notifications_on_lock_screen = True
        print "    Show notifications on lock screen: Yes"
    if current_flags & SUPPRESS_MESSAGE_PREVIEWS:
        print "    Show message preview:              Off"
    elif ((current_flags & SHOW_PREVIEWS_ALWAYS)
            and show_notifications_on_lock_screen):
        print "    Show message preview:              Always"
    if current_flags & DONT_SHOW_IN_CENTER:
        print "    Show in Notification Center:       No"
    else:
        show_count = get_show_count(bundle_id)
        if show_count == 1:
            items = '1 Recent Item'
        else:
            items = '%s Recent Items' % show_count
        print "    Show in Notification Center:       %s" % items
    if current_flags & BADGE_ICONS:
        print "    Badge app icon:                    Yes"
    else:
        print "    Badge app icon:                    No"
    if current_flags & SOUNDS:
        print "    Play sound for notifications:      Yes"
    else:
        print "    Play sound for notifications:      No"


def verify_value_in_allowed(label, value, allowed_values):
    '''Make sure our value has an allowed value'''
    if value not in allowed_values:
        print >> sys.stderr, (
            "%s must be one of: %s."
            % (label, ', '.join(allowed_values)))
        exit(1)


def bundle_ids_or_error_and_exit(bundle_ids):
    '''Print an error and exit if bundle_ids is empty'''
    if not bundle_ids:
        print >> sys.stderr, "Must specify at least one bundle id!"
        exit(1)


def set_alert(style, bundle_ids):
    '''Set the alert style for bundle_id. If kill_nc is False, skip killing
    the NotificationCenter and usernoted processes'''

    # verify this is a supported alert type
    verify_value_in_allowed('Alert style', style, ['none', 'alerts', 'banners'])
    # exit if no bundle_ids were provided
    bundle_ids_or_error_and_exit(bundle_ids)
    for bundle_id in bundle_ids:
        if not bundleid_exists(bundle_id):
            print >> sys.stderr, (
                "WARNING: %s not in Notification Center" % bundle_id)
        else:
            current_flags = get_flags(bundle_id)
            # turn off both banner and alert flags
            new_flags = current_flags & ~(BANNER_STYLE | ALERT_STYLE)
            if style == 'alerts':
                # turn on alert flag
                new_flags = new_flags | ALERT_STYLE
            elif style == 'banners':
                # turn on banner flag
                new_flags = new_flags | BANNER_STYLE
            if new_flags != current_flags:
                set_flags(new_flags, bundle_id)
    kill_notification_center()


def set_show_on_lock_screen(value, bundle_ids):
    '''Set the boolean value for badging the app icon'''

    # verify this is a supported value
    verify_value_in_allowed(
        'Show on lock screen value', value, ['true', 'false'])
    # exit if no bundle_ids were provided
    bundle_ids_or_error_and_exit(bundle_ids)
    for bundle_id in bundle_ids:
        if not bundleid_exists(bundle_id):
            print >> sys.stderr, (
                "WARNING: %s not in Notification Center" % bundle_id)
        else:
            current_flags = get_flags(bundle_id)
            if value == 'true':
                new_flags = (
                    current_flags & ~SUPPRESS_NOTIFICATIONS_ON_LOCKSCREEN)
            else:
                new_flags = current_flags | SUPPRESS_NOTIFICATIONS_ON_LOCKSCREEN
            if new_flags != current_flags:
                set_flags(new_flags, bundle_id)
    kill_notification_center()


def set_badge_app_icon(value, bundle_ids):
    '''Set the boolean value for causing the notifications to be displayed
    when the screen is locked'''

    # verify this is a supported value
    verify_value_in_allowed(
        'Badge app icon value', value, ['true', 'false'])
    # exit if no bundle_ids were provided
    bundle_ids_or_error_and_exit(bundle_ids)
    for bundle_id in bundle_ids:
        if not bundleid_exists(bundle_id):
            print >> sys.stderr, (
                "WARNING: %s not in Notification Center" % bundle_id)
        else:
            current_flags = get_flags(bundle_id)
            if value == 'true':
                new_flags = current_flags | BADGE_ICONS
            else:
                new_flags = current_flags & ~BADGE_ICONS
            if new_flags != current_flags:
                set_flags(new_flags, bundle_id)
    kill_notification_center()


def set_notification_sound(value, bundle_ids):
    '''Set the boolean value for notification sound'''

    # verify this is a supported value
    verify_value_in_allowed(
        'Notification sound value', value, ['true', 'false'])
    # exit if no bundle_ids were provided
    bundle_ids_or_error_and_exit(bundle_ids)
    for bundle_id in bundle_ids:
        if not bundleid_exists(bundle_id):
            print >> sys.stderr, (
                "WARNING: %s not in Notification Center" % bundle_id)
        else:
            current_flags = get_flags(bundle_id)
            if value == 'true':
                new_flags = current_flags | SOUNDS
            else:
                new_flags = current_flags & ~SOUNDS
            if new_flags != current_flags:
                set_flags(new_flags, bundle_id)
    kill_notification_center()


def set_show_in_notification_center(value, bundle_ids):
    '''Set the "Show in Notification Center" options'''

    # verify this is a supported value
    verify_value_in_allowed(
        'Show in notification center value', value, ['0', '1', '5', '10', '20'])
    # exit if no bundle_ids were provided
    bundle_ids_or_error_and_exit(bundle_ids)
    for bundle_id in bundle_ids:
        if not bundleid_exists(bundle_id):
            print >> sys.stderr, (
                "WARNING: %s not in Notification Center" % bundle_id)
        else:
            current_flags = get_flags(bundle_id)
            if value == '0':
                new_flags = current_flags | DONT_SHOW_IN_CENTER
            else:
                conn, curs = connect_to_db()
                curs.execute(
                    "UPDATE app_info SET show_count='%s' where bundleid='%s'"
                     % (value, bundle_id))
                commit_changes(conn)
                new_flags = current_flags & ~DONT_SHOW_IN_CENTER
            if new_flags != current_flags:
                set_flags(new_flags, bundle_id)

    kill_notification_center()


def main():
    '''Define and parse options, call our worker functions'''
    parser = argparse.ArgumentParser(usage=usage())
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='More verbose output from this tool.')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List BUNDLE_IDs in Notification Center database.')

    add_group = parser.add_argument_group(
        'Options for adding or removing apps from Notification Center')
    add_group.add_argument('--insert', '-i', metavar='BUNDLE_ID', nargs='+',
                           help='Add BUNDLE_IDs to Notification Center.')
    add_group.add_argument('--remove', '-r', metavar='BUNDLE_ID', nargs='+',
                           help='Remove BUNDLE_IDs from Notification Center.')
    add_group.add_argument('--remove-system-center', action='store_true',
                           help='Set notification style to \'none\' for all '
                           '_SYSTEM_CENTER_ items.')

    info_group = parser.add_argument_group('Options for getting information')
    info_group.add_argument('--get-alert-style', '-g', metavar='BUNDLE_ID',
                            help=
                            'Get current notification style for BUNDLE_ID.')
    info_group.add_argument('--get-show-on-lock-screen',
                            metavar='BUNDLE_ID',
                            help='Print state of \'Show notifications on lock '
                            'screen\'.')
    info_group.add_argument('--get-badge-app-icon', metavar='BUNDLE_ID',
                            help='Print state of \'Badge app icon\'.')
    info_group.add_argument('--get-sound', metavar='BUNDLE_ID',
                            help=
                            'Print state of \'Play sound for notifications\'.')
    info_group.add_argument('--get-show-in-notification-center',
                            metavar='BUNDLE_ID',
                            help=
                            'Print state of \'Show in Notification Center\'.')
    info_group.add_argument('--get-info', metavar='BUNDLE_ID',
                            help='Print current Notification Center settings '
                            'for BUNDLE_ID.')

    edit_group = parser.add_argument_group('Options for changing settings')
    edit_group.add_argument('--alert-style', '-a',
                            metavar=('ALERT_STYLE BUNDLE_ID', 'BUNDLE_ID'),
                            nargs='+',
                            help='Set notification style for BUNDLE_ID(s). '
                            'Supported styles are none, banners, and alerts.')
    edit_group.add_argument('--show-on-lock-screen',
                            metavar=('true|false BUNDLE_ID', 'BUNDLE_ID'),
                            nargs='+',
                            help='Set display notifications for BUNDLE_ID(s) '
                            'when the screen is locked.')
    edit_group.add_argument('--badge-app-icon',
                            metavar=('true|false BUNDLE_ID', 'BUNDLE_ID'),
                            nargs='+',
                            help='Set badge app icon value for BUNDLE_ID(s).')
    edit_group.add_argument('--sound',
                            metavar=('true|false BUNDLE_ID', 'BUNDLE_ID'),
                            nargs='+',
                            help=
                            'Set notification sound value for BUNDLE_ID(s).')
    edit_group.add_argument('--show-in-notification-center',
                            metavar=('0|1|5|10|20 BUNDLE_ID', 'BUNDLE_ID'),
                            nargs='+',
                            help='Set "Show in Notification Center" options '
                            'for BUNDLE_ID(s).')

    options = parser.parse_args()

    # make sure at least one option has been chosem
    one_attr_set = False
    options_dict = vars(options)
    for key in options_dict.keys():
        if options_dict[key]:
            one_attr_set = True
            break
    if not one_attr_set:
        parser.print_help()
        exit(1)

    # process options
    if options.list:
        list_clients()
    if options.insert:
        insert_app(options.insert)
    if options.remove:
        remove_app(options.remove)
    if options.remove_system_center:
        remove_system_center()
    if options.get_alert_style:
        get_alert_style(options.get_alert_style)
    if options.get_info:
        get_info(options.get_info)
    if options.get_show_on_lock_screen:
        get_show_on_lock_screen(options.get_show_on_lock_screen)
    if options.get_badge_app_icon:
        get_badge_app_icon(options.get_badge_app_icon)
    if options.get_sound:
        get_notification_sound(options.get_sound)
    if options.get_show_in_notification_center:
        get_show_in_notification_center(options.get_show_in_notification_center)
    if options.alert_style:
        set_alert(options.alert_style[0], options.alert_style[1:])
    if options.show_on_lock_screen:
        set_show_on_lock_screen(
            options.show_on_lock_screen[0], options.show_on_lock_screen[1:])
    if options.badge_app_icon:
        set_badge_app_icon(
            options.badge_app_icon[0], options.badge_app_icon[1:])
    if options.sound:
        set_notification_sound(options.sound[0], options.sound[1:])
    if options.show_in_notification_center:
        set_show_in_notification_center(options.show_in_notification_center[0],
                                        options.show_in_notification_center[1:])
if __name__ == "__main__":
    main()
