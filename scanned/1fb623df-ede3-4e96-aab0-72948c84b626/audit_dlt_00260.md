# [M] CL-2021-48: Control Sequence Injector

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: Nimbus, Teku, Prysm, Lighthouse, Lodestar
Published: 2023-05-03
Source: https://notes.ethereum.org/Wg2pH0o3Q1-K2BMowW5vuA
Type: ef-disclosure

## Details
# Log Control Sequence Injection in multiple implementations of the Ethereum 2 beacon node
## Attack scenario
### More detailed description of the attack/bug scenario and unexpected/buggy behaviour
**This report only shows an exploit vector for Nimbus, but 4 more implementations have vulns. We need a way to attach files to send the rest of our PoCs**

An attacker can cause beacon nodes to log control sequences without filtering (Control Sequence Injection). The attacker can manipulate the logs in various ways due to the fact that the strings within log entries are executed by a terminal emulator. This also leads to code execution in some cases, but we will explain that in a future report.
## Impact
### Describe the effect this may have in a production setting
The attacker can put false information in the logs of eth2 beacon nodes. This includes giving a URL for an "update" to the program with malware, or giving malicious instructions. The textual user interface can be modified arbitrarily and there is no way for the user to know the instructions are fake. It's also possible to overwrite log entries nearby the attacker's log entries with things like \r (go back to start of line) and \x1b[NA (go up N lines).
## Components
### Point to the files, functions, and/or specific line numbers where the bug occurs
The logging mechanisms of Prysm, Teku, Lodestar, Lighthouse, and Nimbus.
## Reproduction
### If used any sort of tools/simulations to find the bug, describe in detail how to reproduce the buggy behaviour.
Here is the PoC for Nimbus. The 4 others are long and span multiple files so we will send them when you reply.

A banner will be shown in the Nimbus terminal saying that the user needs to upgrade at https://github.com/fake-nimbus/nimbus/releases/tag/v0.9.10 and its window title will be set to "!! URGENT NOTICE"
A floating banner will also appear on top the Nimbus terminal

Check out commit 8f815074a1afec53464dc569e7dc0cb3af4bec70 of Nimbus
Build it and run the node and view its logs in a terminal
Edit the `target` variable if needed in the following text, save it and run `go run <file>` Tested on Go 1.17

package main

import (
        "encoding/binary"
        "io"
        "net"
)

var target = "127.0.0.1:9000"

func main() {
        for run := 0; run < 2; run++ {
                var c net.Conn
                var err error
                c, err = net.Dial("tcp", target)

_Trimmed to 38 lines — full report: https://notes.ethereum.org/Wg2pH0o3Q1-K2BMowW5vuA_
