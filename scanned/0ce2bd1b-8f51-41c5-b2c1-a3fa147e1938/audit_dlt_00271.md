# [H] CL-2026-03: Nil-pointer dereference in go-multiaddr crashes node via malicious Identify message

## Summary
Severity: High
Chain: Ethereum (consensus layer)
Component: Prysm
Source: https://notes.ethereum.org/vhUgKpoLSOG8KIc1P6yUdg
Type: ef-disclosure

## Details
Short description *
1 sentence description of the bug
A nil-pointer dereference in a Prysm dependency can be used to crash any node, taking just a few network roundtrips and consuming just a tiny amount of bandwidth
Attack scenario *
More detailed description of the attack/bug scenario and unexpected/buggy behaviour
The panic caused by the nil pointer dereference immediately crashes the node. Since this bug goes back such a long time, any Prysm version is affected.

For an attacker, it is easy to trigger this vulnerability by sending /ip6zone/0 to a code path that calls IsIPLoopback or IsIP6LinkLocal. This function is used by a number of callers, most notably in libp2p’s Identify protocol, as used in the exploit code in the proof of concept.

The hardware requirements for this attack are minimal. All that’s required to execute this attack is one (TLS / Noise / QUIC) handshake with the victim, followed by sending of a tiny Identify message. Bandwidth-wise, this attack is exceedingly cheap as well: The data transferred during a typical libp2p handshake is less than 2 kB, and the malicious Identify message is just a few bytes in size. It is trivial to turn this into a sustained attack by repeatedly triggering this panic, in case nodes are automatically restarted after a crash.
Impact *
 Describe the effect this may have in a production setting
An attacker could bring down the entire Prysm part of the network by first compiling a list of nodes and then sending an Identify message containing this malicious multiaddress to every node. It is easy to turn this into a sustained attack by repeatedly contacting nodes that might be automatically rebooted.
Components *
Point to the files, functions, and/or specific line numbers where the bug occurs
The nil-pointer dereference happens in https://github.com/multiformats/go-multiaddr/blob/v0.12.0/net/ip.go#L58-L72. The function works by first:  1. Splitting off the /ip6zone/<zone> component from the address (if any), and then 2. Splitting the first component of the remaining address, and checking if the IP address is a loopback address  However, if the multiaddress only contains an ip6zone component, but nothing after that, the call to zoneless will return nil. Passing nil to SplitFirst will then lead to nil pointer dereference (i.e. a panic). /ip6zone/0 is an example for a multiaddress that would cause this panic.  The exact same reasoning applies to IsIP6LinkLocal.  The faulty code was introduced in October 2018 in this commit, and went unnoticed for more than 5 years.
Reproduction *
If used any sort of tools/simulations to find the bug, describe in detail how to reproduce the buggy behaviour.
Run the following code: go run main.go <victim p2p multiaddr>. 

Note that the stack trace produced by the crash reveals the exact location of the bug, so don’t point this to nodes you don’t control if you don’t want the node operator to know about the vulnerability!

package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/libp2p/go-libp2p"
	"github.com/libp2p/go-libp2p/core/peer"
	"github.com/libp2p/go-libp2p/p2p/protocol/identify"
	"github.com/libp2p/go-libp2p/p2p/protocol/identify/pb"

	"github.com/libp2p/go-msgio/protoio"
	ma "github.com/multiformats/go-multiaddr"
)

_Trimmed to 38 lines — full report: https://notes.ethereum.org/vhUgKpoLSOG8KIc1P6yUdg_
