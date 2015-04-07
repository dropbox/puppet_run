#!/usr/bin/python
# Puppet Wrapper to make sure it runs as expected

import subprocess
import logging
import os
import random
import time

logging.basicConfig(filename='/var/log/puppet_run.log', format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger('puppet_run')

puppet_cmd = ['/usr/bin/puppet', 'agent', '--detailed-exitcodes', '--onetime', '--no-daemonize', '--verbose']
run_lock_file = '/var/lib/puppet/state/agent_catalog_run.lock'
disabled_lock_file = '/var/lib/puppet/state/agent_disabled.lock'
max_delay = 600
env = os.environ.copy()

# This is to workaround a funky launchd issue where it did not pass environment path properly.
if env["PATH"]:
    env["PATH"] = env["PATH"] + ":/usr/local/bin/"
else:
    env["PATH"] = "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin"


def random_delay():
    """Delay the run randomly up to the maximum delay length"""
    randomized_delay = random.randrange(0, max_delay)
    logger.info("Delaying run by %s seconds" % randomized_delay)
    time.sleep(randomized_delay)


def preflight():
    """Make sure there isn't a hung puppet run or disabled puppet agent. If there is, kill it and remove the lock file"""
    logger.info("Running Puppet Preflight Actions...")

    if os.path.exists(run_lock_file):
        logger.info("Agent Run Lock file is present, cleaning up previous run...")
        old_pid = read_pidfile(run_lock_file)
        os.remove(run_lock_file)
        if check_for_process(old_pid):
            os.kill(int(old_pid), 9)

    if os.path.exists(disabled_lock_file):
        logger.info("Agent Disabled Lock file is present, cleaning up previous run...")
        old_pid = read_pidfile(disabled_lock_file)
        os.remove(disabled_lock_file)
        if check_for_process(old_pid):
            os.kill(int(old_pid), 9)


def read_pidfile(pidfile):
    """Read pidfile from the given path"""
    if os.path.exists(pidfile):
        with file(pidfile) as f:
            pid = f.read()
            f.close()
        result = pid.rstrip('\n')
    else:
        result = None

    return result


def check_for_process(pid):
    """Check if process is running and return pid if it is running"""
    if pid:
        cmd = ['/bin/ps', '-p', pid, '-o', 'pid=']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, error_output) = proc.communicate()
        return output.rstrip('\n')
    else:
        return None


def run_puppet():
    """Actually do the puppet run"""
    returncode = 1

    logger.info("Running Puppet...")
    returncode = subprocess.call(puppet_cmd, env=env)

    if returncode != 0:
        returncode = subprocess.call(puppet_cmd, env=env)

    logger.info("Puppet run finished with exit code %s" % returncode)


def main():
    random_delay()
    preflight()
    run_puppet()


if __name__ == "__main__":
    main()
