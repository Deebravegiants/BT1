# [?] fix(header/p2p): fix crash in server (#1569)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2023-01-05
Source: https://github.com/celestiaorg/celestia-node/commit/92904dc5c4f2235fddc9de2768252967ca8422b8
Type: security-commit

## Details
fix(header/p2p): fix crash in server (#1569)

## Overview
Resolves #1564 + small fixes in the peerTracker
## Checklist
- [x] Required CI checks are passing
- [x] Visual proof for any user facing features like CLI or
documentation updates
- [x] Linked issues closed with keywords

## Patch
### header/p2p/exchange.go
```diff
@@ -74,14 +74,14 @@ func NewExchange(
 func (ex *Exchange) Start(context.Context) error {
 	ex.ctx, ex.cancel = context.WithCancel(context.Background())
 
-	go ex.peerTracker.gc()
-	go ex.peerTracker.track()
 	for _, p := range ex.trustedPeers {
 		// Try to pre-connect to trusted peers.
 		// We don't really care if we succeed at this point
 		// and just need any peers in the peerTracker asap
 		go ex.host.Connect(ex.ctx, peer.AddrInfo{ID: p}) //nolint:errcheck
 	}
+	go ex.peerTracker.gc()
+	go ex.peerTracker.track()
 	return nil
 }
 
```

### header/p2p/exchange_test.go
```diff
@@ -311,9 +311,11 @@ func createP2PExAndServer(t *testing.T, host, tpeer libhost.Host) (*Exchange, *h
 	require.NoError(t, err)
 	ex, err := NewExchange(host, []peer.ID{tpeer.ID()}, "private", connGater)
 	require.NoError(t, err)
-	ex.peerTracker.trackedPeers[tpeer.ID()] = &peerStat{peerID: tpeer.ID(), peerScore: 100}
 	require.NoError(t, ex.Start(context.Background()))
-
+	time.Sleep(time.Millisecond * 100) // give peerTracker time to add a trusted peer
+	ex.peerTracker.peerLk.Lock()
+	ex.peerTracker.trackedPeers[tpeer.ID()] = &peerStat{peerID: tpeer.ID(), peerScore: 100.0}
+	ex.peerTracker.peerLk.Unlock()
 	t.Cleanup(func() {
 		serverSideEx.Stop(context.Background()) //nolint:errcheck
 		ex.Stop(context.Background())           //nolint:errcheck
```

### header/p2p/server.go
```diff
@@ -135,7 +135,7 @@ func (serv *ExchangeServer) requestHandler(stream network.Stream) {
 		}
 		_, err = serde.Write(stream, &p2p_pb.ExtendedHeaderResponse{Body: bin, StatusCode: code})
 		if err != nil {
-			log.Errorw("server: writing header to stream", "height", h.Height, "err", err)
+			log.Errorw("server: writing header to stream", "err", err)
 			stream.Reset() //nolint:errcheck
 			return
 		}
```
