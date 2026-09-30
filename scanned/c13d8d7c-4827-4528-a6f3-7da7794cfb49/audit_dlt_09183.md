# [?] autorelay: fix race condition in TestBackoff (#1731)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2022-09-06
Source: https://github.com/libp2p/go-libp2p/commit/cb8c25f5d9d7b1428278cf952d703282d29a8cd4
Type: security-commit

## Details
autorelay: fix race condition in TestBackoff (#1731)

## Patch
### p2p/host/autorelay/autorelay_test.go
```diff
@@ -239,11 +239,11 @@ func TestBackoff(t *testing.T) {
 		str.Reset()
 	})
 
-	var counter int
+	var counter int32 // to be used atomically
 	h := newPrivateNode(t,
 		autorelay.WithPeerSource(func(int) <-chan peer.AddrInfo {
 			// always return the same node, and make sure we don't try to connect to it too frequently
-			counter++
+			atomic.AddInt32(&counter, 1)
 			peerChan := make(chan peer.AddrInfo, 1)
 			peerChan <- peer.AddrInfo{ID: r.ID(), Addrs: r.Addrs()}
 			close(peerChan)
@@ -264,7 +264,7 @@ func TestBackoff(t *testing.T) {
 	}
 	cl.Add(backoff / 2)
 	require.Eventually(t, func() bool { return atomic.LoadInt32(&reservations) == 2 }, 3*time.Second, 20*time.Millisecond)
-	require.Less(t, counter, 100) // just make sure we're not busy-looping
+	require.Less(t, int(atomic.LoadInt32(&counter)), 100) // just make sure we're not busy-looping
 	require.Equal(t, 2, int(atomic.LoadInt32(&reservations)))
 }
 
```
