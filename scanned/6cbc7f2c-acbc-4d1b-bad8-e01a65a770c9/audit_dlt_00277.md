# [H] CL-2026-09: Gossipsub malformed topic hex decoding panic crashes node

## Summary
Severity: High
Chain: Ethereum (consensus layer)
Component: Prysm
Source: https://notes.ethereum.org/3iUKrEptRu-KijxRGxRSMw
Type: ef-disclosure

## Details
Short description *
1 sentence description of the bug
An attacker can crash any Prysm node by sending a single malicious Gossipsub message, allowing it to bring down large parts of the Ethereum network with minimal cost. The attacker does not need to be in a priviliged position in the network.
Attack scenario *
More detailed description of the attack/bug scenario and unexpected/buggy behaviour
An attacker can join the network and, over the course of hours or even days, create a list of Prysm nodes and their address(es). He can then connect to these nodes all at once and send the malicious payload, immediately crashing a large fraction of the Ethereum network.

Since it doesn't require a privileged position in the network, it is possible to pull off this attack from a newly spawned virtual machine. Furthermore, the amount of resources needed is absolutely minimal, since the main cost of this attack (both in terms of CPU and in terms of bandwidth) is performing a single TLS or Noise handshake with the victim. The malicious payload itself is tiny (less than 100 bytes).

The attacker could run this attack continuously, in order to immediately crash any nodes that might have been restarted.
Impact *
 Describe the effect this may have in a production setting
This bug is reminiscent of the multiaddr parsing panic I reported in early 2024, which also allowed an attacker to trigger a panic by sending a short malformed payload.

There's no way to mitigate this attack, and if deployed in the wild, node operators would have to install a patch to protect their nodes.
Components *
Point to the files, functions, and/or specific line numbers where the bug occurs
The standard library contains a function to perform hex decoding of a source slice `src`  into a destination slice `dst`: `encoding/hex.Decode(dst, src []byte) (int, error)` . This function expects `dst` to be exactly half the size of `src`, and `src` to have an even length. Crucially, this function panics if `len(src) > len(dst)/2` due to an out-of-bounds memory access.  This function is used when processing the Gossipsub topic in https://github.com/OffchainLabs/prysm/blob/v6.1.1/beacon-chain/p2p/pubsub_filter.go#L78-L90. Specifically, `dst` is a 4-byte byte slice here, and therefore the panic can be triggered by (for example) a `src` input of 10 bytes.  ---  One might argue that this is a bug in the standard library, and the respective length check should be performed there.  In the spirit of defensive programming, I'd be sympathetic to such an argument, especially since this check is not very costly. However, the standard library authors seem to disagree, see this discussion from 2019: https://github.com/golang/go/issues/34982.  As things stand, it is the caller's responsibility to check that `len(dst) == hex.DecodedLen(len(src))`.
Reproduction *
If used any sort of tools/simulations to find the bug, describe in detail how to reproduce the buggy behaviour.
package main

import (
	"context"
	"log"
	"os"
	"time"

	"github.com/libp2p/go-libp2p"
	pubsub "github.com/libp2p/go-libp2p-pubsub"
	"github.com/libp2p/go-libp2p/core/host"
	"github.com/libp2p/go-libp2p/core/network"
	"github.com/libp2p/go-libp2p/core/peer"
	"github.com/libp2p/go-libp2p/p2p/security/noise"

	"github.com/OffchainLabs/prysm/v6/beacon-chain/db/kv"
	ethp2p "github.com/OffchainLabs/prysm/v6/beacon-chain/p2p"
	"github.com/OffchainLabs/prysm/v6/beacon-chain/startup"

_Trimmed to 38 lines — full report: https://notes.ethereum.org/3iUKrEptRu-KijxRGxRSMw_
