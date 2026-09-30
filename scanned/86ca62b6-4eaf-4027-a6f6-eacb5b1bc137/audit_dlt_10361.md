# [?] fetcher: fix race condition todo

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-10-15
Source: https://github.com/0xsoniclabs/sonic/commit/1e35068e878fe4b1433168f53559902ff5c19b11
Type: security-commit

## Details
fetcher: fix race condition todo

## Patch
### gossip/fetcher/fetcher.go
```diff
@@ -10,6 +10,7 @@ import (
 	"github.com/Fantom-foundation/go-lachesis/hash"
 	"github.com/Fantom-foundation/go-lachesis/inter"
 	"github.com/Fantom-foundation/go-lachesis/logger"
+	"github.com/Fantom-foundation/go-lachesis/utils"
 )
 
 /*
@@ -90,9 +91,11 @@ type Fetcher struct {
 	callback Callback
 
 	// Announce states
+	stateMu   utils.SpinLock                // Protects announces and announced
 	announces map[string]int                // Per peer announce counts to prevent memory exhaustion
 	announced map[hash.Event][]*oneAnnounce // Announced events, scheduled for fetching
-	fetching  map[hash.Event]*oneAnnounce   // Announced events, currently fetching
+
+	fetching map[hash.Event]*oneAnnounce // Announced events, currently fetching
 
 	logger.Periodic
 }
@@ -136,15 +139,37 @@ func (f *Fetcher) Stop() {
 	f.callback.HeavyCheck.Stop()
 }
 
+// Overloaded returns true if too much events are being processed or requested
 func (f *Fetcher) Overloaded() bool {
+	f.stateMu.Lock()
+	defer f.stateMu.Unlock()
+	return f.overloaded()
+}
+
+func (f *Fetcher) overloaded() bool {
 	return len(f.inject) > maxQueuedInjects*3/4 ||
 		len(f.notify) > maxQueuedAnns*3/4 ||
-		len(f.announced) > hashLimit ||
+		len(f.announced) > hashLimit || // protected by stateMu
 		f.callback.HeavyCheck.Overloaded()
 }
 
+// Overloaded returns true if too much events are being processed or requested from the peer
 func (f *Fetcher) OverloadedPeer(peer string) bool {
-	return f.Overloaded() || f.announces[peer] > hashLimit/2 // TODO must be synced
+	f.stateMu.Lock()
+	defer f.stateMu.Unlock()
+	return f.overloaded() || f.announces[peer] > hashLimit/2 // protected by stateMu
+}
+
+func (f *Fetcher) setAnnounces(peer string, num int) {
+	f.stateMu.Lock()
+	defer f.stateMu.Unlock()
+	f.announces[peer] = num
+}
+
+func (f *Fetcher) setAnnounced(id hash.Event, announces []*oneAnnounce) {
+	f.stateMu.Lock()
+	defer f.stateMu.Unlock()
+	f.announced[id] = announces
 }
 
 // Notify announces the fetcher of the potential availability of a new event in
@@ -275,15 +300,15 @@ func (f *Fetcher) loop() {
 					batch: notification,
 					i:     i,
 				}
-				f.announced[id] = append(f.announced[id], ann)
+				f.setAnnounced(id, append(f.announced[id], ann))
 				count++ // f.announced and f.announces must be synced!
 				// if it wasn't announced before, then schedule for fetching this time
 				if _, ok := f.fetching[id]; !ok {
 					f.fetching[id] = ann
 					toFetch.Add(id)
 				}
 			}
-			f.announces[notification.peer] = count
+			f.setAnnounces(notification.peer, count)
 
 			if len(toFetch) != 0 {
 				err := notification.fetchEvents(toFetch)
@@ -394,6 +419,9 @@ func (f *Fetcher) rescheduleFetch(fetch *time.Timer) {
 // forgetHash removes all traces of a event announcement from the fetcher's
 // internal state.
 func (f *Fetcher) forgetHash(hash hash.Event) {
+	f.stateMu.Lock()
+	defer f.stateMu.Unlock()
+
 	// Remove all pending announces and decrement DOS counters
 	for _, announce := range f.announced[hash] {
 		f.announces[announce.batch.peer]--
```

### utils/spin_lock.go
```diff
@@ -0,0 +1,37 @@
+package utils
+
+import (
+	"runtime"
+	"sync/atomic"
+)
+
+// SpinLock implements a simple atomic spin lock, the zero value for a SpinLock is an unlocked spinlock.
+type SpinLock struct {
+	f uint32
+}
+
+// Lock locks sl. If the lock is already in use, the caller blocks until Unlock is called
+func (sl *SpinLock) Lock() {
+	for !sl.TryLock() {
+		runtime.Gosched() // allow other goroutines to do work.
+	}
+}
+
+// Unlock unlocks sl, unlike [Mutex.Unlock](http://golang.org/pkg/sync/#Mutex.Unlock),
+// there's no harm calling it on an unlocked SpinLock
+func (sl *SpinLock) Unlock() {
+	atomic.StoreUint32(&sl.f, 0)
+}
+
+// TryLock will try to lock sl and return whether it succeed or not without blocking.
+func (sl *SpinLock) TryLock() bool {
+	return atomic.CompareAndSwapUint32(&sl.f, 0, 1)
+}
+
+// String is human readable lock state
+func (sl *SpinLock) String() string {
+	if atomic.LoadUint32(&sl.f) == 1 {
+		return "Locked"
+	}
+	return "Unlocked"
+}
```
