# [H] CL-2020-29: Libp2p identify-delta add-protocols spam - force OOM within a minute

## Summary
Severity: High
Chain: Ethereum (consensus layer)
Component: Prysm
Published: 2021-12-01
Source: https://github.com/ethereum/public-disclosures/blob/master/disclosures/CL-2021-12-01.md
Type: ef-disclosure

## Details
# libp2p identify DoS

Disclosure to Protocol Labs & Libp2p core. DoS vector found by @protolambda.

The problem: streaming a "delta" in identification info: malefactor can push without rate-limit, and protocols get accumulated into in-memory peerstore.
[Libp2p delta implementation](https://github.com/libp2p/go-libp2p/blob/fcf69647e945b30851fe394d140f7a70643e48cf/p2p/protocol/identify/id_delta.go#L17)

The libp2p identify information is put into the peerstore by default, which is a memory peerstore by default.
The Prysm Eth2 client has been updated to disable the delta-protocol until it is safe to use again.

The delta identify stream processes 2048 bytes at a time, but is not rate limited, and all protocols are added to the existing peerstore records.
Without expiration of protocols, pruning, validity checks, or sanity checks of any kind.

The result is that an attacker can feed a Go Libp2p node until the node goes OOM.
The most efficient approach found so far creates a 10x amplification in bandwidth vs. memory consumed.

Below is a test-case to reproduce an attack on a node efficiently, with log info about memory usage:

```go
package identify

import (
	"github.com/fjl/memsize"
    //...
)

func TestService_identifyDoS(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	sk1, _, err := coretest.RandTestKeyPair(ic.RSA, 4096)
	require.NoError(t, err)
	sk2, _, err := coretest.RandTestKeyPair(ic.RSA, 4096)
	require.NoError(t, err)

	hA := blhost.NewBlankHost(swarmt.GenSwarm(t, ctx, swarmt.OptPeerPrivateKey(sk1)))
	hB := blhost.NewBlankHost(swarmt.GenSwarm(t, ctx, swarmt.OptPeerPrivateKey(sk2)))

```

_Trimmed to 38 lines — full report: https://github.com/ethereum/public-disclosures/blob/master/disclosures/CL-2021-12-01.md_
