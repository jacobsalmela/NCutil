#!/usr/bin/python
##############################
######### IMPORTS ############
import sqlite3
import sys
import getopt
import os
import pwd
import grp
from platform import mac_ver

##############################
######## VARIABLES ###########
# Store OS X version in format of 10.x
v, _, _ = mac_ver()
v = float('.'.join(v.split('.')[:2]))

username = 'your_user'
unique_db = '12345678-ABCD-1234-5D6F-9876543210.db'

#uid = pwd.getpwnam("nobody").pw_uid
#gid = grp.getgrnam("nogroup").gr_gid

nc_db = '/Users/' + username + '/Library/Application Support/NotificationCenter/' + unique_db

conn = sqlite3.connect(nc_db)
conn.text_factory = str
c = conn.cursor()

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
    print "                                     "
    print "USAGE:--------------------"
    print "                                     "
    print "	%s -h [--help]" % (name,)
    #print "	%s -v [--verbose]" % (name,)
    print "	%s -l [--list]" % (name,)
    print "	%s -i [--insert] <bundle id>" % (name,)
    print "	%s -r [--remove] <bundle id>" % (name,)
    print "	%s -a [--alertstyle] <bundle id> banner|alert " % (name,)
    print ""

	
def commit_changes():
	#------------------------
	# Apply the changes and close the sqlite connection
	conn.commit()
	conn.close()
	#os.chown(nc_db, uid, gid)


def verboseOutput(*args):
	#------------------------
	if verbose:
		try:
			print "Verbose:", args
		except:
			pass
 
	
def list_clients():
	#------------------------
	c.execute("select * from app_info")
	for row in c.fetchall():
		print row[1]

		
def get_available_id():
	#------------------------
	c.execute("select * from app_info")
	last_iteration = None
	for row in c.fetchall():
		if last_iteration is not None:
			pass
		last_iteration = 'no'
	last_id = row[0]
	return last_id + 1
		

def insert_app(bundle_id):
	#------------------------
	last_id = get_available_id()
	c.execute("INSERT or REPLACE INTO app_info VALUES('%s', '%s', '14', '5', '%s')" % (last_id, bundle_id, last_id))
	commit_changes()
	
	
def remove_app(bundle_id):
	#------------------------
	c.execute("DELETE from app_info where bundleid IS '%s'" % (bundle_id))
	commit_changes()
	
	
def set_alert_style(bundle_id, style):
	#------------------------
	alert_style = ""
	if style == "banner":
		alert_style = "14"
	elif style == "alert":
		alert_style = "14"
	else:
		print "Not a valid alert type"
		
	c.execute("UPDATE app_info SET flags='%s' where bundleid='%s'" % (bundle_id, alert_style))
	commit_changes()

	

#------------------------
#------------------------
#------------------------
def main():
	#------------------------
	#------------------------
	#------------------------
	try:
		# First arguments are UNIX-style, single-letter arguments
		# Second list are long options.  Those requiring arguments are followed by an =

		
		
		opts, args = getopt.getopt(sys.argv[1::], "hlvi:r:a:", ["help", "list", "verbose", "insert=", "remove=", "alertstyle="])
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
		elif o in ("-a", "--alertstyle"):
			for arg in args:
				set_alert_style(a, arg)
		else:
			assert False, "unhandled option"
		
		
		


if __name__ == "__main__":
	main()
