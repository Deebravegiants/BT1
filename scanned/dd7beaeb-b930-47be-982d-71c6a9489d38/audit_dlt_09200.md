# [?] fix panic in observed address activation check

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2019-04-09
Source: https://github.com/libp2p/go-libp2p/commit/a4776e6174b4c4a1d67138785be4c382aadb5406
Type: security-commit

## Details
fix panic in observed address activation check

The activated check cleans up, which leads to panics with concurrent reads.
This moves the seenBy set clean up into gc, where it belongs

## Patch
### p2p/protocol/identify/obsaddr.go
```diff
@@ -31,15 +31,6 @@ type ObservedAddr struct {
 }
 
 func (oa *ObservedAddr) activated(ttl time.Duration) bool {
-	// cleanup SeenBy set
-	now := time.Now()
-
-	for k, ob := range oa.SeenBy {
-		if now.Sub(ob.seenTime) > ttl*ActivationThresh {
-			delete(oa.SeenBy, k)
-		}
-	}
-
 	// We only activate if in the TTL other peers observed the same address
 	// of ours at least 4 times.
 	return len(oa.SeenBy) >= ActivationThresh
@@ -154,7 +145,15 @@ func (oas *ObservedAddrSet) gc() {
 	for local, observedAddrs := range oas.addrs {
 		// TODO we can do this without allocating by compacting the array in place
 		filteredAddrs := make([]*ObservedAddr, 0, len(observedAddrs))
+
 		for _, a := range observedAddrs {
+			// clean up SeenBy set
+			for k, ob := range a.SeenBy {
+				if now.Sub(ob.seenTime) > oas.ttl*ActivationThresh {
+					delete(a.SeenBy, k)
+				}
+			}
+
 			// leave only alive observed addresses
 			if now.Sub(a.LastSeen) <= oas.ttl {
 				filteredAddrs = append(filteredAddrs, a)
```
