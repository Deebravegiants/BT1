# [?] fix nil dereference

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2018-01-20
Source: https://github.com/libp2p/go-libp2p/commit/48221760c6128bcb1e86de789fb6b0ccba823f8e
Type: security-commit

## Details
fix nil dereference

## Patch
### p2p/net/upgrader/listener.go
```diff
@@ -96,8 +96,8 @@ func (l *listener) handleIncoming() {
 				// to completely negotiate the connection.
 				log.Debugf("accept upgrade error: %s (%s <--> %s)",
 					err,
-					conn.LocalMultiaddr(),
-					conn.RemoteMultiaddr())
+					maconn.LocalMultiaddr(),
+					maconn.RemoteMultiaddr())
 				return
 			}
 
```
