# [?] relay: fix deadlock when closing (#2171)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2023-03-05
Source: https://github.com/libp2p/go-libp2p/commit/43fd678024952f9b71e99376588518f99c198ec2
Type: security-commit

## Details
relay: fix deadlock when closing (#2171)

* fix deadlock on relay service close

* clean up background go routine too

* increase test timeout

## Patch
### p2p/host/relaysvc/relay_test.go
```diff
@@ -34,7 +34,7 @@ func TestReachabilityChangeEvent(t *testing.T) {
 	require.Eventually(
 		t,
 		func() bool { rmgr.mutex.Lock(); defer rmgr.mutex.Unlock(); return rmgr.relay == nil },
-		1*time.Second,
+		3*time.Second,
 		100*time.Millisecond,
 		"relay should be nil on private reachability")
 
@@ -45,7 +45,7 @@ func TestReachabilityChangeEvent(t *testing.T) {
 	require.Eventually(
 		t,
 		func() bool { rmgr.mutex.Lock(); defer rmgr.mutex.Unlock(); return rmgr.relay == nil },
-		1*time.Second,
+		3*time.Second,
 		100*time.Millisecond,
 		"relay should be nil on unknown reachability")
 
```

### p2p/protocol/circuitv2/relay/relay.go
```diff
@@ -51,6 +51,7 @@ type Relay struct {
 	constraints *constraints
 	scope       network.ResourceScopeSpan
 	notifiee    network.Notifiee
+	wg          sync.WaitGroup
 
 	mx     sync.Mutex
 	rsvp   map[peer.ID]time.Time
@@ -98,24 +99,27 @@ func New(h host.Host, opts ...Option) (*Relay, error) {
 	h.SetStreamHandler(proto.ProtoIDv2Hop, r.handleStream)
 	r.notifiee = &network.NotifyBundle{DisconnectedF: r.disconnected}
 	h.Network().Notify(r.notifiee)
+
+	r.wg.Add(1)
 	go r.background()
 
 	return r, nil
 }
 
 func (r *Relay) Close() error {
 	r.mx.Lock()
-	defer r.mx.Unlock()
 	if !r.closed {
 		r.closed = true
+		r.mx.Unlock()
+
 		r.host.RemoveStreamHandler(proto.ProtoIDv2Hop)
 		r.host.Network().StopNotify(r.notifiee)
 		r.scope.Done()
 		r.cancel()
-		for p := range r.rsvp {
-			r.host.ConnManager().UntagPeer(p, "relay-reservation")
-		}
+		r.wg.Wait()
+		return nil
 	}
+	r.mx.Unlock()
 	return nil
 }
 
@@ -564,6 +568,8 @@ func (r *Relay) background() {
 		case <-ticker.C:
 			r.gc()
 		case <-r.ctx.Done():
+			r.gc()
+			r.wg.Done()
 			return
 		}
 	}
@@ -576,7 +582,7 @@ func (r *Relay) gc() {
 	now := time.Now()
 
 	for p, expire := range r.rsvp {
-		if expire.Before(now) {
+		if r.closed || expire.Before(now) {
 			delete(r.rsvp, p)
 			r.host.ConnManager().UntagPeer(p, "relay-reservation")
 		}
```
