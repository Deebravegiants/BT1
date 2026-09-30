# [?] fix race condition in notifications test

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2015-07-20
Source: https://github.com/libp2p/go-libp2p/commit/57e6cb40bde928680e8c484c720209c651734427
Type: security-commit

## Details
fix race condition in notifications test

License: MIT
Signed-off-by: Jeromy <jeromyj@gmail.com>

## Patch
### net/mock/mock_notif_test.go
```diff
@@ -7,6 +7,7 @@ import (
 	ma "github.com/ipfs/go-ipfs/Godeps/_workspace/src/github.com/jbenet/go-multiaddr"
 	context "github.com/ipfs/go-ipfs/Godeps/_workspace/src/golang.org/x/net/context"
 	inet "github.com/ipfs/go-ipfs/p2p/net"
+	peer "github.com/ipfs/go-ipfs/p2p/peer"
 )
 
 func TestNotifications(t *testing.T) {
@@ -42,31 +43,29 @@ func TestNotifications(t *testing.T) {
 	// test everyone got the correct connection opened calls
 	for i, s := range nets {
 		n := notifiees[i]
-		for _, s2 := range nets {
-			var actual []inet.Conn
-			for len(s.ConnsToPeer(s2.LocalPeer())) != len(actual) {
-				select {
-				case c := <-n.connected:
-					actual = append(actual, c)
-				case <-time.After(timeout):
-					t.Fatal("timeout")
+		notifs := make(map[peer.ID]inet.Conn)
+		for j := 0; j < len(nets)-1; j++ {
+			select {
+			case c := <-n.connected:
+				_, ok := notifs[c.RemotePeer()]
+				if ok {
+					t.Fatal("shouldnt have received more than one connection per peer")
 				}
+				notifs[c.RemotePeer()] = c
+			case <-time.After(timeout):
+				t.Fatal("timeout")
 			}
+		}
 
-			expect := s.ConnsToPeer(s2.LocalPeer())
-			for _, c1 := range actual {
-				found := false
-				for _, c2 := range expect {
-					if c1 == c2 {
-						found = true
-						break
-					}
-				}
-				if !found {
-					t.Error("connection not found", c1, len(expect), len(actual))
-				}
+		for p, con := range notifs {
+			expect := s.ConnsToPeer(p)
+			if len(expect) != 1 {
+				t.Fatal("got more than one connection, not supposed to happen")
 			}
 
+			if expect[0] != con {
+				t.Fatal("got different connection than we expected")
+			}
 		}
 	}
 
```
