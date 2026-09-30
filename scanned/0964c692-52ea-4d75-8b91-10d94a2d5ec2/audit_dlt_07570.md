# [?] p2p/tracker: fix crash in clean when tracker is stopped (#33940)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-03-03
Source: https://github.com/ethereum/go-ethereum/commit/9962e2c9f33a666d634a0d3cb90478b608cf8b46
Type: security-commit

## Details
p2p/tracker: fix crash in clean when tracker is stopped (#33940)

## Patch
### p2p/tracker/tracker.go
```diff
@@ -138,6 +138,10 @@ func (t *Tracker) clean() {
 	t.lock.Lock()
 	defer t.lock.Unlock()
 
+	if t.expire == nil {
+		return // Tracker was stopped.
+	}
+
 	// Expire anything within a certain threshold (might be no items at all if
 	// we raced with the delivery)
 	for t.expire.Len() > 0 {
@@ -162,14 +166,15 @@ func (t *Tracker) clean() {
 	t.schedule()
 }
 
-// schedule starts a timer to trigger on the expiration of the first network
-// packet.
+// schedule starts a timer to trigger on the expiration of the first network packet.
 func (t *Tracker) schedule() {
 	if t.expire.Len() == 0 {
 		t.wake = nil
 		return
 	}
-	t.wake = time.AfterFunc(time.Until(t.pending[t.expire.Front().Value.(uint64)].time.Add(t.timeout)), t.clean)
+	nextID := t.expire.Front().Value.(uint64)
+	nextTime := t.pending[nextID].time
+	t.wake = time.AfterFunc(time.Until(nextTime.Add(t.timeout)), t.clean)
 }
 
 // Stop reclaims resources of the tracker.
```

### p2p/tracker/tracker_test.go
```diff
@@ -24,6 +24,25 @@ import (
 	"github.com/ethereum/go-ethereum/p2p"
 )
 
+// TestCleanAfterStop verifies that the clean method does not crash when called
+// after Stop. This can happen because clean is scheduled via time.AfterFunc and
+// may fire after Stop sets t.expire to nil.
+func TestCleanAfterStop(t *testing.T) {
+	cap := p2p.Cap{Name: "test", Version: 1}
+	timeout := 50 * time.Millisecond
+	tr := New(cap, "peer1", timeout)
+
+	// Track a request to start the expiration timer.
+	tr.Track(Request{ID: 1, ReqCode: 0x01, RespCode: 0x02, Size: 1})
+
+	// Stop the tracker, then wait for the timer to fire.
+	tr.Stop()
+	time.Sleep(timeout + 50*time.Millisecond)
+
+	// Also verify that calling clean directly after stop doesn't panic.
+	tr.clean()
+}
+
 // This checks that metrics gauges for pending requests are be decremented when a
 // Tracker is stopped.
 func TestMetricsOnStop(t *testing.T) {
```
