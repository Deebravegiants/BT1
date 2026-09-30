# [?] conn: connection ID, fix RemoteMultiaddr panic

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2017-07-17
Source: https://github.com/libp2p/go-libp2p/commit/37e58194250f31d57158779cf2504c84624e2a97
Type: security-commit

## Details
conn: connection ID, fix RemoteMultiaddr panic

## Patch
### p2p/protocol/internal/circuitv1-deprecated/conn.go
```diff
@@ -42,7 +42,7 @@ func (c *Conn) RemoteAddr() net.Addr {
 }
 
 func (c *Conn) RemoteMultiaddr() ma.Multiaddr {
-	a, err := ma.NewMultiaddr(fmt.Sprintf("/ipfs/%s/p2p-circuit/%s", c.remote.ID.Pretty(), c.Conn().RemotePeer()))
+	a, err := ma.NewMultiaddr(fmt.Sprintf("/ipfs/%s/p2p-circuit/ipfs/%s", c.remote.ID.Pretty(), c.Conn().RemotePeer().Pretty()))
 	if err != nil {
 		panic(err)
 	}
@@ -83,5 +83,5 @@ func (c *Conn) RemotePublicKey() ic.PubKey {
 }
 
 func (c *Conn) ID() string {
-	return "TODO: relay conn ID"
+	return iconn.ID(c)
 }
```
