# [?] fix(share/discovery): deadlock in limitedSet (#2190)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2023-05-13
Source: https://github.com/celestiaorg/celestia-node/commit/9baade4bd0300dabcd160c185e145a824c128e30
Type: security-commit

## Details
fix(share/discovery): deadlock in limitedSet (#2190)

The deadlock eventually blocks the disconnect event processing in Discovery, causing libp2p connection processing to stall. It was discovered via libp2p metrics

## Patch
### share/availability/discovery/discovery.go
```diff
@@ -210,11 +210,8 @@ func (d *Discovery) disconnectsLoop(ctx context.Context, sub event.Subscription)
 				return
 			}
 
-			if evnt := e.(event.EvtPeerConnectednessChanged); evnt.Connectedness == network.NotConnected {
-				if !d.set.Contains(evnt.Peer) {
-					continue
-				}
-
+			evnt := e.(event.EvtPeerConnectednessChanged)
+			if evnt.Connectedness == network.NotConnected && d.set.Contains(evnt.Peer) {
 				d.host.ConnManager().Unprotect(evnt.Peer, rendezvousPoint)
 				d.connector.Backoff(evnt.Peer)
 				d.set.Remove(evnt.Peer)
```

### share/availability/discovery/set.go
```diff
@@ -47,6 +47,7 @@ func (ps *limitedSet) Size() uint {
 func (ps *limitedSet) Add(p peer.ID) (added bool) {
 	ps.lk.Lock()
 	if _, ok := ps.ps[p]; ok {
+		ps.lk.Unlock()
 		return false
 	}
 	ps.ps[p] = struct{}{}
@@ -65,10 +66,8 @@ func (ps *limitedSet) Add(p peer.ID) (added bool) {
 
 func (ps *limitedSet) Remove(id peer.ID) {
 	ps.lk.Lock()
-	defer ps.lk.Unlock()
-	if ps.limit > 0 {
-		delete(ps.ps, id)
-	}
+	delete(ps.ps, id)
+	ps.lk.Unlock()
 }
 
 // Peers returns all discovered peers from the set.
```
