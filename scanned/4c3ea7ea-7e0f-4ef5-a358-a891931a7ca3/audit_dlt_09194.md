# [?] fix race condition in TestActiveRelay

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2021-07-10
Source: https://github.com/libp2p/go-libp2p/commit/d5fa138e023466e6f3057f4562e2f1d0ff32d6c0
Type: security-commit

## Details
fix race condition in TestActiveRelay

## Patch
### p2p/protocol/internal/circuitv1-deprecated/relay_test.go
```diff
@@ -19,6 +19,7 @@ import (
 	swarm "github.com/libp2p/go-libp2p-swarm"
 	swarmt "github.com/libp2p/go-libp2p-swarm/testing"
 	ma "github.com/multiformats/go-multiaddr"
+	manet "github.com/multiformats/go-multiaddr/net"
 )
 
 /* TODO: add tests
@@ -395,43 +396,27 @@ func TestActiveRelay(t *testing.T) {
 	time.Sleep(10 * time.Millisecond)
 
 	r1 := newTestRelay(t, ctx, hosts[0])
-
 	newTestRelay(t, ctx, hosts[1], OptHop, OptActive)
-
 	r3 := newTestRelay(t, ctx, hosts[2])
 
-	var (
-		conn1, conn2 net.Conn
-		done         = make(chan struct{})
-	)
-
-	defer func() {
-		<-done
-		if conn1 != nil {
-			conn1.Close()
-		}
-		if conn2 != nil {
-			conn2.Close()
-		}
-	}()
+	connChan := make(chan manet.Conn)
 
 	msg := []byte("relay works!")
 	go func() {
-		defer close(done)
+		defer close(connChan)
 		list := r3.Listener()
 
-		var err error
-		conn2, err = list.Accept()
+		conn1, err := list.Accept()
 		if err != nil {
 			t.Error(err)
 			return
 		}
 
-		_, err = conn2.Write(msg)
-		if err != nil {
+		if _, err := conn1.Write(msg); err != nil {
 			t.Error(err)
 			return
 		}
+		connChan <- conn1
 	}()
 
 	rinfo := hosts[1].Peerstore().PeerInfo(hosts[1].ID())
@@ -440,11 +425,11 @@ func TestActiveRelay(t *testing.T) {
 	rctx, rcancel := context.WithTimeout(ctx, time.Second)
 	defer rcancel()
 
-	var err error
-	conn2, err = r1.DialPeer(rctx, rinfo, dinfo)
+	conn2, err := r1.DialPeer(rctx, rinfo, dinfo)
 	if err != nil {
 		t.Fatal(err)
 	}
+	defer conn2.Close()
 
 	data := make([]byte, len(msg))
 	_, err = io.ReadFull(conn2, data)
@@ -455,6 +440,11 @@ func TestActiveRelay(t *testing.T) {
 	if !bytes.Equal(data, msg) {
 		t.Fatal("message was incorrect:", string(data))
 	}
+	conn1, ok := <-connChan
+	if !ok {
+		t.Fatal("listener didn't accept a connection")
+	}
+	conn1.Close()
 }
 
 func TestRelayCanHop(t *testing.T) {
```
