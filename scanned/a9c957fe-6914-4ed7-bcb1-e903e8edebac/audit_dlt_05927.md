# [?] fix(autonatv2): don't panic in GetReachability after Close

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2026-07-22
Source: https://github.com/libp2p/go-libp2p/commit/f23601bf34bc8f440fe27ec61b41dee81f5cf1eb
Type: security-commit

## Details
fix(autonatv2): don't panic in GetReachability after Close

Close set an.peers = nil without holding an.mx while GetReachability
reads it under the lock: an unsynchronized write, and a nil pointer
panic in peersMap.Shuffled for callers racing with Close. The host
closes autonat before the address manager, so the reachability
tracker's probe workers can issue checks in exactly that window,
crashing the process during shutdown.

Guard the write with the mutex and return ErrNoPeers once closed;
the reachability tracker treats ErrNoPeers as persistent and backs
off its workers.

Assisted-By: Claude Fable 5

## Patch
### p2p/protocol/autonatv2/autonat.go
```diff
@@ -174,7 +174,9 @@ func (an *AutoNAT) Close() {
 	an.wg.Wait()
 	an.srv.Close()
 	an.cli.Close()
+	an.mx.Lock()
 	an.peers = nil
+	an.mx.Unlock()
 }
 
 // GetReachability makes a single dial request for checking reachability for requested addresses
@@ -196,6 +198,11 @@ func (an *AutoNAT) GetReachability(ctx context.Context, reqs []Request) (Result,
 		filteredReqs = reqs
 	}
 	an.mx.Lock()
+	// nil after Close; host shutdown can have in-flight reachability checks
+	if an.peers == nil {
+		an.mx.Unlock()
+		return Result{}, ErrNoPeers
+	}
 	now := time.Now()
 	var p peer.ID
 	for pr := range an.peers.Shuffled() {
```

### p2p/protocol/autonatv2/autonat_test.go
```diff
@@ -97,6 +97,16 @@ func TestAutoNATPrivateAddr(t *testing.T) {
 	require.ErrorIs(t, err, ErrPrivateAddrs)
 }
 
+func TestGetReachabilityAfterClose(t *testing.T) {
+	// The host closes autonat before the address manager, whose reachability
+	// tracker workers may still issue checks during shutdown.
+	an := newAutoNAT(t, nil)
+	an.Close()
+	res, err := an.GetReachability(context.Background(), []Request{{Addr: ma.StringCast("/ip4/1.2.3.4/udp/10/quic-v1")}})
+	require.ErrorIs(t, err, ErrNoPeers)
+	require.Equal(t, Result{}, res)
+}
+
 func TestClientRequest(t *testing.T) {
 	an := newAutoNAT(t, nil, AllowPrivateAddrs)
 	defer an.Close()
```
