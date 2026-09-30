# [?] p2p/discover: fix deadlock in discv5 message dispatch (#21858)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2020-11-25
Source: https://github.com/celo-org/celo-blockchain/commit/429e7141f2f41c1d66dd4dd711a47ca9e0f0c2cb
Type: security-commit

## Details
p2p/discover: fix deadlock in discv5 message dispatch (#21858)

This fixes a deadlock that could occur when a response packet arrived
after a call had already received enough responses and was about to
signal completion to the dispatch loop.

Co-authored-by: Felix Lange <fjl@twurst.com>

## Patch
### p2p/discover/v5_udp.go
```diff
@@ -454,9 +454,20 @@ func (t *UDPv5) call(node *enode.Node, responseType byte, packet v5wire.Packet)
 
 // callDone tells dispatch that the active call is done.
 func (t *UDPv5) callDone(c *callV5) {
-	select {
-	case t.callDoneCh <- c:
-	case <-t.closeCtx.Done():
+	// This needs a loop because further responses may be incoming until the
+	// send to callDoneCh has completed. Such responses need to be discarded
+	// in order to avoid blocking the dispatch loop.
+	for {
+		select {
+		case <-c.ch:
+			// late response, discard.
+		case <-c.err:
+			// late error, discard.
+		case t.callDoneCh <- c:
+			return
+		case <-t.closeCtx.Done():
+			return
+		}
 	}
 }
 
```
