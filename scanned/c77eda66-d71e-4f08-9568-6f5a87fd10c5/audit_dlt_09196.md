# [?] fix a potential nil-pointer panic. (#158)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2020-05-22
Source: https://github.com/libp2p/go-libp2p/commit/029459e4c9ad64660143141e7607b55ebc214e6d
Type: security-commit

## Details
fix a potential nil-pointer panic. (#158)

## Patch
### p2p/transport/quic/filtered_conn.go
```diff
@@ -51,7 +51,7 @@ func (c *filteredConn) ReadFrom(b []byte) (n int, addr net.Addr, rerr error) {
 
 		connAddrs := &connAddrs{lmAddr: c.lmAddr, rmAddr: rmAddr}
 
-		if c.gater.InterceptAccept(connAddrs) {
+		if c.gater != nil && c.gater.InterceptAccept(connAddrs) {
 			return
 		}
 	}
```
