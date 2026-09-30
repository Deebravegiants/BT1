# [?] quic: fix race condition when generating random holepunch packet (#2263)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2023-04-27
Source: https://github.com/libp2p/go-libp2p/commit/ed8a07dd4f3d1a25822287a483055bc0e6cc0701
Type: security-commit

## Details
quic: fix race condition when generating random holepunch packet (#2263)

## Patch
### p2p/transport/quic/transport.go
```diff
@@ -45,7 +45,9 @@ type transport struct {
 
 	holePunchingMx sync.Mutex
 	holePunching   map[holePunchKey]*activeHolePunch
-	rnd            rand.Rand
+
+	rndMx sync.Mutex
+	rnd   rand.Rand
 
 	connMx sync.Mutex
 	conns  map[quic.Connection]*conn
@@ -218,7 +220,10 @@ func (t *transport) holePunch(ctx context.Context, raddr ma.Multiaddr, p peer.ID
 	var punchErr error
 loop:
 	for i := 0; ; i++ {
-		if _, err := t.rnd.Read(payload); err != nil {
+		t.rndMx.Lock()
+		_, err := t.rnd.Read(payload)
+		t.rndMx.Unlock()
+		if err != nil {
 			punchErr = err
 			break
 		}
```
