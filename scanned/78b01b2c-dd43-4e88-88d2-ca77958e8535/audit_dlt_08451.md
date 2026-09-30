# [?] fix(discovery): remove panic in switch statement (#4526)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2025-09-08
Source: https://github.com/celestiaorg/celestia-node/commit/ee13d6edbf85e32c05f4dc9ac787ed74083861b2
Type: security-commit

## Details
fix(discovery): remove panic in switch statement (#4526)

## Patch
### share/shwap/p2p/discovery/discovery.go
```diff
@@ -353,7 +353,8 @@ func (d *Discovery) handleDiscoveredPeer(ctx context.Context, peer peer.AddrInfo
 		return false
 	}
 
-	switch d.host.Network().Connectedness(peer.ID) {
+	connectedness := d.host.Network().Connectedness(peer.ID)
+	switch connectedness {
 	case network.Connected:
 		d.connector.Backoff(peer.ID) // we still have to backoff the connected peer
 	case network.NotConnected:
@@ -365,11 +366,13 @@ func (d *Discovery) handleDiscoveredPeer(ctx context.Context, peer peer.AddrInfo
 		}
 		if err != nil {
 			d.metrics.observeHandlePeer(ctx, handlePeerConnErr)
-			logger.Debugw("unable to connect", "err", err)
+			logger.Debugw("skip handle: unable to connect", "err", err)
 			return false
 		}
 	default:
-		panic("unknown connectedness")
+		logger.Warnw("skip handle: unsupported status", "peer", peer.ID.String(), "status", connectedness.String())
+		d.metrics.observeHandlePeer(ctx, handlePeerUnknownStatus)
+		return false
 	}
 
 	if !d.set.Add(peer.ID) {
```

### share/shwap/p2p/discovery/metrics.go
```diff
@@ -15,13 +15,14 @@ import (
 const (
 	discoveryEnoughPeersKey = "enough_peers"
 
-	handlePeerResultKey                    = "result"
-	handlePeerSkipSelf    handlePeerResult = "skip_self"
-	handlePeerEnoughPeers handlePeerResult = "skip_enough_peers"
-	handlePeerBackoff     handlePeerResult = "skip_backoff"
-	handlePeerConnected   handlePeerResult = "connected"
-	handlePeerConnErr     handlePeerResult = "conn_err"
-	handlePeerInSet       handlePeerResult = "in_set"
+	handlePeerResultKey                      = "result"
+	handlePeerSkipSelf      handlePeerResult = "skip_self"
+	handlePeerEnoughPeers   handlePeerResult = "skip_enough_peers"
+	handlePeerBackoff       handlePeerResult = "skip_backoff"
+	handlePeerConnected     handlePeerResult = "connected"
+	handlePeerConnErr       handlePeerResult = "conn_err"
+	handlePeerInSet         handlePeerResult = "in_set"
+	handlePeerUnknownStatus handlePeerResult = "unknown_status"
 
 	advertiseFailedKey = "failed"
 )
```
