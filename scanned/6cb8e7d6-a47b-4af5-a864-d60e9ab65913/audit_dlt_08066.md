# [?] whisper: Fix race condition in whisperv6/peer.go

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-02-20
Source: https://github.com/celo-org/celo-blockchain/commit/34d94e22d9c9f3c2373a398269ecbba0139827d2
Type: security-commit

## Details
whisper: Fix race condition in whisperv6/peer.go

## Patch
### whisper/whisperv6/peer.go
```diff
@@ -19,6 +19,7 @@ package whisperv6
 import (
 	"fmt"
 	"math"
+	"sync"
 	"time"
 
 	"github.com/ethereum/go-ethereum/common"
@@ -36,6 +37,7 @@ type Peer struct {
 
 	trusted        bool
 	powRequirement float64
+	bloomMu        sync.Mutex
 	bloomFilter    []byte
 	fullNode       bool
 
@@ -225,10 +227,14 @@ func (peer *Peer) notifyAboutBloomFilterChange(bloom []byte) error {
 }
 
 func (peer *Peer) bloomMatch(env *Envelope) bool {
+	peer.bloomMu.Lock()
+	defer peer.bloomMu.Unlock()
 	return peer.fullNode || bloomFilterMatch(peer.bloomFilter, env.Bloom())
 }
 
 func (peer *Peer) setBloomFilter(bloom []byte) {
+	peer.bloomMu.Lock()
+	defer peer.bloomMu.Unlock()
 	peer.bloomFilter = bloom
 	peer.fullNode = isFullNode(bloom)
 	if peer.fullNode && peer.bloomFilter == nil {
```
