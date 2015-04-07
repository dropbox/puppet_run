# puppet_run
A wrapper script and launchd for running open source puppet

To use this wrapper, do the following:

* Place puppet_run.py into /usr/local/bin and make sure it has execute permissions
* Edit com.company.puppet_run.plist to match your company name, as well as the Label key inside the plist.
* Place the launchd .plist into /Library/LaunchDaemons with the correct permissions
* Load the launchd and you should get puppet runs every 15 minutes, randomized as to not thrash the server.

Note: You can make it run less frequently by increasing the StartInterval in the launchd and max_delay variable in puppet_run.py.
