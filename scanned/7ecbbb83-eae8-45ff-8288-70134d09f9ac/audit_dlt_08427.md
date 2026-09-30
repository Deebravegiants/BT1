# [?] fix nil pointer panic by checking if peer is nil

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2018-06-29
Source: https://github.com/cometbft/cometbft/commit/9752e059e1ca10e0a7a2e130fd9ce4b97d1a6e1a
Type: security-commit

## Details
fix nil pointer panic by checking if peer is nil

Fixes #1830

remember that PeerSet#Get can return nil

## Patch
### p2p/peer_set.go
```diff
@@ -55,17 +55,17 @@ func (ps *PeerSet) Add(peer Peer) error {
 	return nil
 }
 
-// Has returns true iff the PeerSet contains
-// the peer referred to by this peerKey.
+// Has returns true if the set contains the peer referred to by this
+// peerKey, otherwise false.
 func (ps *PeerSet) Has(peerKey ID) bool {
 	ps.mtx.Lock()
 	_, ok := ps.lookup[peerKey]
 	ps.mtx.Unlock()
 	return ok
 }
 
-// HasIP returns true if the PeerSet contains the peer referred to by this IP
-// address.
+// HasIP returns true if the set contains the peer referred to by this IP
+// address, otherwise false.
 func (ps *PeerSet) HasIP(peerIP net.IP) bool {
 	ps.mtx.Lock()
 	defer ps.mtx.Unlock()
@@ -85,7 +85,8 @@ func (ps *PeerSet) hasIP(peerIP net.IP) bool {
 	return false
 }
 
-// Get looks up a peer by the provided peerKey.
+// Get looks up a peer by the provided peerKey. Returns nil if peer is not
+// found.
 func (ps *PeerSet) Get(peerKey ID) Peer {
 	ps.mtx.Lock()
 	defer ps.mtx.Unlock()
```

### p2p/pex/pex_reactor.go
```diff
@@ -77,10 +77,10 @@ type PEXReactor struct {
 	attemptsToDial sync.Map // address (string) -> {number of attempts (int), last time dialed (time.Time)}
 }
 
-func (pexR *PEXReactor) minReceiveRequestInterval() time.Duration {
+func (r *PEXReactor) minReceiveRequestInterval() time.Duration {
 	// NOTE: must be less than ensurePeersPeriod, otherwise we'll request
 	// peers too quickly from others and they'll think we're bad!
-	return pexR.ensurePeersPeriod / 3
+	return r.ensurePeersPeriod / 3
 }
 
 // PEXReactorConfig holds reactor specific configuration data.
@@ -628,7 +628,9 @@ func (r *PEXReactor) crawlPeers() {
 		}
 		// Ask for more addresses
 		peer := r.Switch.Peers().Get(pi.Addr.ID)
-		r.RequestAddrs(peer)
+		if peer != nil {
+			r.RequestAddrs(peer)
+		}
 	}
 }
 
```
