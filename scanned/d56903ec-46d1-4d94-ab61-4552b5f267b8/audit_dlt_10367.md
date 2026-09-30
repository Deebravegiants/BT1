# [?] data race fix

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-08-26
Source: https://github.com/0xsoniclabs/sonic/commit/84bcb5472cd89a182b29107e18349175893c0285
Type: security-commit

## Details
data race fix

## Patch
### src/gossip/handler.go
```diff
@@ -392,8 +392,8 @@ func (pm *ProtocolManager) handleMsg(p *peer) error {
 		if len(progress.LastPackInfo.Heads) > hardLimitItems {
 			return errResp(ErrMsgTooLarge, "%v", msg)
 		}
-		p.progress = progress
-		if p.progress.Epoch == myEpoch {
+		p.SetProgress(progress)
+		if progress.Epoch == myEpoch {
 			atomic.StoreUint32(&pm.synced, 1) // Mark initial sync done on any peer which has the same epoch
 		}
 
```

### src/gossip/peer.go
```diff
@@ -61,8 +61,6 @@ type peer struct {
 	version  int         // Protocol version negotiated
 	syncDrop *time.Timer // Timed connection dropper if sync progress isn't validated in time
 
-	lock sync.RWMutex
-
 	knownTxs    mapset.Set                // Set of transaction hashes known to be known by this peer
 	knownEvents mapset.Set                // Set of event hashes known to be known by this peer
 	queuedTxs   chan []*types.Transaction // Queue of transactions to broadcast to the peer
@@ -71,13 +69,27 @@ type peer struct {
 	term        chan struct{}             // Termination channel to stop the broadcaster
 
 	progress PeerProgress
+
+	sync.RWMutex
 }
 
-func (p *PeerProgress) InterestedIn(eventEpoch idx.Epoch) bool {
-	if p.Epoch == 0 || eventEpoch == 0 {
-		return false
-	}
-	return eventEpoch == p.Epoch || eventEpoch == p.Epoch+1
+func (p *peer) SetProgress(x PeerProgress) {
+	p.Lock()
+	defer p.Unlock()
+
+	p.progress = x
+}
+
+func (p *peer) InterestedIn(h hash.Event) bool {
+	e := h.Epoch()
+
+	p.RLock()
+	defer p.RUnlock()
+
+	return e != 0 &&
+		p.progress.Epoch != 0 &&
+		(e == p.progress.Epoch || e == p.progress.Epoch+1) &&
+		!p.knownEvents.Contains(h)
 }
 
 func (a *PeerProgress) Less(b PeerProgress) bool {
@@ -480,13 +492,13 @@ func (ps *peerSet) Len() int {
 
 // PeersWithoutEvent retrieves a list of peers that do not have a given event in
 // their set of known hashes.
-func (ps *peerSet) PeersWithoutEvent(hash hash.Event) []*peer {
+func (ps *peerSet) PeersWithoutEvent(e hash.Event) []*peer {
 	ps.lock.RLock()
 	defer ps.lock.RUnlock()
 
 	list := make([]*peer, 0, len(ps.peers))
 	for _, p := range ps.peers {
-		if p.progress.InterestedIn(hash.Epoch()) && !p.knownEvents.Contains(hash) {
+		if p.InterestedIn(e) {
 			list = append(list, p)
 		}
 	}
```

### src/gossip/protocol.go
```diff
@@ -1,14 +1,16 @@
 package gossip
 
 import (
-	"github.com/Fantom-foundation/go-lachesis/src/hash"
-	"github.com/Fantom-foundation/go-lachesis/src/inter/idx"
+	"math/big"
+
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/core"
 	"github.com/ethereum/go-ethereum/core/types"
 	"github.com/ethereum/go-ethereum/event"
 	"github.com/ethereum/go-ethereum/rlp"
-	"math/big"
+
+	"github.com/Fantom-foundation/go-lachesis/src/hash"
+	"github.com/Fantom-foundation/go-lachesis/src/inter/idx"
 )
 
 // Constants to match up protocol versions and messages
```
