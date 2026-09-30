# [?] Prevent data race in allowWindowIncrease (#259)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2022-02-07
Source: https://github.com/libp2p/go-libp2p/commit/add734f37438b1cbc64f942a6647f31dcaa5f944
Type: security-commit

## Details
Prevent data race in allowWindowIncrease (#259)

## Patch
### p2p/transport/quic/transport.go
```diff
@@ -381,7 +381,9 @@ func (t *transport) allowWindowIncrease(sess quic.Session, size uint64) bool {
 	// into our connections map (which we do right after dialing / accepting it),
 	// we have no way to account for that memory. This should be very rare.
 	// Block this attempt. The session can request more memory later.
+	t.connMx.Lock()
 	c, ok := t.conns[sess]
+	t.connMx.Unlock()
 	if !ok {
 		return false
 	}
```
