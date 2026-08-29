# [H] CL-2026-07: Unbounded memory consumption in libp2p protocol book via Identify Push

## Summary
Severity: High
Chain: Ethereum (consensus layer)
Component: Prysm
Source: https://notes.ethereum.org/e_nZZJ84S_6_-xF9WzW9gw
Type: ef-disclosure

## Details
Short description *
1 sentence description of the bug
Unbounded memory consumption in libp2p protocol book
Attack scenario *
More detailed description of the attack/bug scenario and unexpected/buggy behaviour
The libp2p protocol book contains logic to deduplicate the strings used for libp2p protocol names. Every protocol is inserted into a map, so that future references to the same protocol don't need to allocate the string again. However, there's no sanity check performed on the protocols inserted into this map, nor is the map garbage collected or limited in size.

An attacker can therefore generate random strings and make the victim (permanently!) insert these strings into this map. A convenient way to do so is using Identify Push, which allows the attacker to send up to 8 kB of protocol strings per stream. Note that it is possible to open an unlimited number of Identify Push streams, as long as it's done sequentially (the resource manager would protect against concurrently opening a large number of Identify Push streams).
Impact *
 Describe the effect this may have in a production setting
An attacker can easily bring down Prysm nodes by consuming all their available memory. As described above, this requires sending as much data over the network as the node has memory (although in practice, I measured a slight amplification of ~1.5). The attacker can run this attack from multiple vantage points in the network. The bottleneck of the attack will then be the available bandwidth of the victim. On a standard 1 GBit/s connection the attacker can therefore consume 7.5 GB of RAM per minute. It's feasible to bring down large parts of the network by combining the bandwidth of multiple attacker-controlled nodes.
Components *
Point to the files, functions, and/or specific line numbers where the bug occurs
The map in https://github.com/libp2p/go-libp2p/blob/v0.35.1/p2p/host/peerstore/pstoremem/protobook.go#L31 is never gc-ed. The vulnerability was introduced in 2019 in https://github.com/libp2p/go-libp2p-peerstore/pull/79.
Reproduction *
If used any sort of tools/simulations to find the bug, describe in detail how to reproduce the buggy behaviour.
    package main
    
    import (
    	"context"
    	"fmt"
    	"io"
    	"log"
    	"os"
    
    	"golang.org/x/exp/rand"
    
    	"github.com/libp2p/go-libp2p"
    	"github.com/libp2p/go-libp2p/core/network"
    	"github.com/libp2p/go-libp2p/core/peer"
    	"github.com/libp2p/go-libp2p/p2p/protocol/identify"
    	"github.com/libp2p/go-libp2p/p2p/protocol/identify/pb"
    	"github.com/libp2p/go-msgio/pbio"
    	ma "github.com/multiformats/go-multiaddr"
    )
    
    const maxSize = 8<<10 - 100 // maximum size of Identify message, leaving some space for Protobuf encoding overhead
    

_Trimmed to 38 lines — full report: https://notes.ethereum.org/e_nZZJ84S_6_-xF9WzW9gw_
