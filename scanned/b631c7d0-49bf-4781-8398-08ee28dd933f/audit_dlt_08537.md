# [?] network: fix publicKeyIdentTracker data race in hybrid mode (#6110)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2024-08-26
Source: https://github.com/algorand/go-algorand/commit/499007787f522af16781b3f3e43a70b3516ea7e3
Type: security-commit

## Details
network: fix publicKeyIdentTracker data race in hybrid mode (#6110)

## Patch
### network/netidentity.go
```diff
@@ -23,6 +23,7 @@ import (
 
 	"github.com/algorand/go-algorand/crypto"
 	"github.com/algorand/go-algorand/protocol"
+	"github.com/algorand/go-deadlock"
 )
 
 // netidentity.go implements functionality to participate in an "Identity Challenge Exchange"
@@ -461,12 +462,14 @@ func (noopIdentityTracker) removeIdentity(p *wsPeer)   {}
 // mapping from PublicKeys exchanged in identity challenges to a peer
 // this structure is not thread-safe; it is protected by wn.peersLock or p2p.wsPeersLock
 type publicKeyIdentTracker struct {
+	mu        deadlock.Mutex
 	peersByID map[crypto.PublicKey]*wsPeer
 }
 
 // NewIdentityTracker returns a new publicKeyIdentTracker
 func NewIdentityTracker() *publicKeyIdentTracker {
 	return &publicKeyIdentTracker{
+		mu:        deadlock.Mutex{},
 		peersByID: make(map[crypto.PublicKey]*wsPeer),
 	}
 }
@@ -475,6 +478,8 @@ func NewIdentityTracker() *publicKeyIdentTracker {
 // returns false if it was unable to load the peer into the given identity
 // or true otherwise (if the peer was already there, or if it was added)
 func (t *publicKeyIdentTracker) setIdentity(p *wsPeer) bool {
+	t.mu.Lock()
+	defer t.mu.Unlock()
 	existingPeer, exists := t.peersByID[p.identity]
 	if !exists {
 		// the identity is not occupied, so set it and return true
@@ -489,6 +494,8 @@ func (t *publicKeyIdentTracker) setIdentity(p *wsPeer) bool {
 // removeIdentity removes the entry in the peersByID map if it exists
 // and is occupied by the given peer
 func (t *publicKeyIdentTracker) removeIdentity(p *wsPeer) {
+	t.mu.Lock()
+	defer t.mu.Unlock()
 	if t.peersByID[p.identity] == p {
 		delete(t.peersByID, p.identity)
 	}
```
