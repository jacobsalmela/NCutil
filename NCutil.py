#!/usr/bin/python
##############################
######### IMPORTS ############
import sqlite3
import sys
import getopt
import os
import pwd
import grp
import subprocess
from platform import mac_ver
from getpass import getuser
from glob import glob


##############################
######## FUNCTIONS ###########
def usage(e=None):
    #------------------------
    name = os.path.basename(sys.argv[0])
    print "  _  _  ___     _   _ _ "
    print " | \| |/ __|  _| |_(_) |"
    print " | .` | (_| || |  _| | |"
    print " |_|\_|\___\_,_|\__|_|_|"
    print "                                     "
    print "Copyright 2014. Jacob Salmela.  http://jacobsalmela.com"
    print "Modified + OSX 10.10 Yosemite Support,  Jason Johnson (2015)"
    print "                                              "
    print "USAGE:--------------------"
    print " %s -h [--help]" % (name,)
    #print "    %s -v [--verbose]" % (name,)
    print " %s -l [--list]" % (name,)
    print " %s -i [--insert] <bundle id>" % (name,)
    print " %s -r [--remove] <bundle id>" % (name,)
    print " %s -s [--remove-system-center] " % (name,)
    print " %s -a [--alertstyle] <bundle id> none|banners|alerts " % (name,)
    print ""


def get_nc_db():
    '''Returns a path to the current(?) NotificationCenter db'''
    nc_db = None
    # Store OS X version in format of 10.x.x
    v, _, _ = mac_ver()
    #Parse Out Major Version, mac_ver() can produce 10.10.2, 10.9.5, 10.8..
    osx_major = v.split('.')[0] + "." + v.split('.')[1]

    if (osx_major == '10.8') or (osx_major == '10.9'):
        nc_nb_path = os.path.expanduser(
            '~/Library/Application Support/NotificationCenter/')
        nc_dbs = glob(nc_nb_path + '*.db')
        if nc_dbs:
            nc_dbs.sort(key=os.path.getmtime)
            # most recently modified will be the last one
            nc_db = nc_dbs[-1]
    # Support for osx 10.10 added via randomly generated id for Notification Center Database
    elif (osx_major == '10.10'):
        darwin_user_dir = subprocess.check_output(
            ['/usr/bin/getconf', 'DARWIN_USER_DIR']).rstrip()
        nc_db = os.path.join(
            darwin_user_dir, 'com.apple.notificationcenter/db/db')
    return nc_db


def connect_to_db():
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
    subprocess.call(['/usr/bin/killall', 'NotificationCenter'])
    subprocess.call(['/usr/bin/killall', 'usernoted'])


def commit_changes(conn):
    #------------------------
    # Apply the changes and close the sqlite connection
    conn.commit()
    conn.close()
    kill_notification_center()
    
    


def verboseOutput(*args):
    #------------------------
    if verbose:
        try:
            print "Verbose:", args
        except:
            pass


def list_clients():
    #------------------------
    conn, curs = connect_to_db()
    curs.execute("select * from app_info")
    for row in curs.fetchall():
        print row[1]
    conn.close()


def get_available_id(curs):
    #------------------------
    curs.execute("select * from app_info")
    last_iteration = None
    for row in c.fetchall():
        if last_iteration is not None:
            pass
        last_iteration = 'no'
    last_id = row[0]
    return last_id + 1


def insert_app(bundle_id):
    #------------------------
    conn, curs = connect_to_db()
    last_id = get_available_id(curs)
    curs.execute("INSERT or REPLACE INTO app_info VALUES('%s', '%s', '14', '5', '%s')" % (last_id, bundle_id, last_id))
    commit_changes(conn)


def remove_app(bundle_id):
    #------------------------
    conn, curs = connect_to_db()
    if (bundle_id == 'com.apple.maspushagent') or (bundle_id == 'com.apple.appstore'):
        print "Yeah, those alerts are annoying."
    curs.execute("DELETE from app_info where bundleid IS '%s'" % (bundle_id))
    commit_changes(conn)


def set_alert_style(alert_style, bundle_id, like=False):
    #------------------------
    conn, curs = connect_to_db()
    if like:
        curs.execute("UPDATE app_info SET flags='%s' where bundleid like '%s'" % (alert_style, bundle_id))
    else:
        curs.execute("UPDATE app_info SET flags='%s' where bundleid='%s'" % (alert_style, bundle_id))
        commit_changes(conn)


def get_alert_style(alert_style, bundle_id):
    #------------------------
    conn, curs = connect_to_db()
    curs.execute("SELECT flags from app_info where bundleid='%d'" % (alert_style))
    conn.close()


def remove_system_center():
    if osx_major == "10.10":
        set_alert_style("12609", "_SYSTEM_CENTER_%", True)


def set_alert(bundle_id, style):
    #------------------------

    # verify this is a supported alert type
    if style not in ['none', 'alerts', 'banners']:
        print "Not a valid alert type"
        exit(1)

    #Build Bundle Types
    bundles = {}
    bundles['com.apple.mail'] = {'10.10': {'alerts': 342, 'banners': 334, 'none': 20801}, '10.9': {'alerts': 86, 'banners': 78}}
    bundles['com.apple.iCal'] = {'10.10': {'alerts': 8566, 'banners': 8558, 'none': 12641}, '10.9': {'alerts': 8310, 'banners': 8302}}
    bundles['com.apple.iChat'] = {'10.10': {'alerts': 86, 'banners': 78, 'none': 20801}, '10.9': {'alerts': 10443, 'banners': 78}}
    bundles['default'] = {'10.10': {'alerts': 8534, 'banners': 8526, 'none': 12609}, '10.9': {'alerts': 86, 'banners': 1239}}

    if osx_major == "10.10":
        if bundle_id in bundles:
            set_alert_style(bundles[bundle_id][osx_major][style], bundle_id)
        else:
            set_alert_style(bundles['default'][osx_major][style], bundle_id)
    else:
        if style == "none":
            print "10.9 & 10.8 style None is not currently supported"
        else:
            if bundle_id in bundles:
                set_alert_style(bundles[bundle_id][osx_major][style], bundle_id)
            else:
                set_alert_style(bundles['default'][osx_major][style], bundle_id)


def main():
    # ------------------------
    #------------------------
    #------------------------
    try:
        # First arguments are UNIX-style, single-letter arguments
        # Second list are long options.  Those requiring arguments are followed by an =
        opts, args = getopt.getopt(sys.argv[1::], "hlvi:r:a:s",
                                   ["help", "list", "verbose", "remove-system-center", "insert=", "remove=", "alertstyle="])
    except getopt.GetoptError as err:
        usage()
        sys.exit(2)
    verbose = False

    # Parse arguments for options
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-l", "--list"):
            list_clients()
        elif o in ("-v", "--verbose"):
            verbose = True
            print "Verbose feature to be added at a later date."
        elif o in ("-i", "--insert"):
            insert_app(a)
        elif o in ("-r", "--remove"):
            remove_app(a)
        elif o in ("-s", "--remove-system-center"):
            remove_system_center()
        elif o in ("-a", "--alertstyle"):
            for arg in args:
                set_alert(a, arg)
        else:
            assert False, "unhandled option"

if __name__ == "__main__":
    main()
