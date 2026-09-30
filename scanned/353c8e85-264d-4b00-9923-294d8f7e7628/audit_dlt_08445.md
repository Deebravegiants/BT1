# [?] shrex/peers: Avoid cooldown lock-order deadlock (#5179)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2026-09-15
Source: https://github.com/celestiaorg/celestia-node/commit/5e0bac31ff333e7221963cf97607aa18f44757b3
Type: security-commit

## Details
shrex/peers: Avoid cooldown lock-order deadlock (#5179)

Co-authored-by: renaynay <41963722+renaynay@users.noreply.github.com>

## Patch
### share/shwap/p2p/shrex/peers/metrics.go
```diff
@@ -148,7 +148,7 @@ func initMetrics(manager *Manager) (*metrics, error) {
 		observer.ObserveInt64(discoveredPool, int64(manager.nodes.len()),
 			metric.WithAttributes(
 				attribute.String(peerStatusKey, string(peerStatusActive))))
-		observer.ObserveInt64(discoveredPool, int64(manager.nodes.cooldown.len()),
+		observer.ObserveInt64(discoveredPool, int64(manager.nodes.cooldownLen()),
 			metric.WithAttributes(
 				attribute.String(peerStatusKey, string(peerStatusCooldown))))
 
```

### share/shwap/p2p/shrex/peers/pool.go
```diff
@@ -46,7 +46,7 @@ func newPool(peerCooldownTime time.Duration, stats *peerStats) *pool {
 		hasPeerCh:        make(chan struct{}),
 		cleanupThreshold: defaultCleanupThreshold,
 	}
-	p.cooldown = newTimedQueue(peerCooldownTime, p.afterCooldown)
+	p.cooldown = newTimedQueue(peerCooldownTime, p.releaseCooldown)
 	return p
 }
 
@@ -140,6 +140,7 @@ func (p *pool) remove(peers ...peer.ID) {
 	for _, peerID := range peers {
 		if status, ok := p.statuses[peerID]; ok && status != removed {
 			p.statuses[peerID] = removed
+			p.cooldown.remove(peerID)
 			if status == active {
 				p.activeCount--
 			}
@@ -202,20 +203,24 @@ func (p *pool) putOnCooldown(peerID peer.ID) {
 	}
 }
 
-func (p *pool) afterCooldown(peerID peer.ID) {
+// releaseCooldown holds the pool lock while removing entries and updating peer states.
+func (p *pool) releaseCooldown() {
 	p.m.Lock()
 	defer p.m.Unlock()
 
-	// item could have been already removed by the time afterCooldown is called
-	if status, ok := p.statuses[peerID]; !ok || status != cooldown {
-		return
-	}
-
-	p.statuses[peerID] = active
-	p.activeCount++
+	p.cooldown.releaseExpired(func(peerID peer.ID) {
+		p.statuses[peerID] = active
+		p.activeCount++
+	})
 	p.checkHasPeers()
 }
 
+func (p *pool) cooldownLen() int {
+	p.m.RLock()
+	defer p.m.RUnlock()
+	return p.cooldown.len()
+}
+
 // checkHasPeers will check and indicate if there are peers in the pool.
 func (p *pool) checkHasPeers() {
 	if p.activeCount > 0 && !p.hasPeer {
```

### share/shwap/p2p/shrex/peers/pool_test.go
```diff
@@ -2,9 +2,11 @@ package peers
 
 import (
 	"context"
+	"sync"
 	"testing"
 	"time"
 
+	"github.com/benbjohnson/clock"
 	"github.com/libp2p/go-libp2p/core/peer"
 	"github.com/stretchr/testify/require"
 )
@@ -211,4 +213,63 @@ func TestPool(t *testing.T) {
 		_, ok := p.tryGet()
 		require.False(t, ok)
 	})
+
+	t.Run("remove pending cooldown", func(t *testing.T) {
+		peerID := peer.ID("peer1")
+		mock := clock.NewMock()
+		p := newTestPool(t, time.Second)
+		p.cooldown.clock = mock
+		p.add(peerID)
+		p.putOnCooldown(peerID)
+		p.remove(peerID)
+		p.m.RLock()
+		require.Zero(t, p.cooldown.len())
+		p.m.RUnlock()
+	})
+
+	t.Run("stale timer after removal and new cooldown", func(t *testing.T) {
+		peerID := peer.ID("peer1")
+		mock := clock.NewMock()
+		p := newTestPool(t, time.Second)
+		p.cooldown.clock = mock
+		p.add(peerID)
+		p.putOnCooldown(peerID)
+		mock.Add(time.Second / 2)
+		p.remove(peerID)
+		p.add(peerID)
+		p.putOnCooldown(peerID)
+		mock.Add(time.Second / 2)
+
+		// A stopped timer can already be waiting for the pool lock.
+		p.releaseCooldown()
+		require.Zero(t, p.len())
+		require.Equal(t, 1, p.cooldownLen())
+
+		mock.Add(time.Second / 2)
+		require.Equal(t, 1, p.len())
+		require.Zero(t, p.cooldownLen())
+		p.releaseCooldown()
+		require.Equal(t, 1, p.len())
+	})
+
+	t.Run("concurrent cooldown and removal", func(t *testing.T) {
+		peerID := peer.ID("peer1")
+		p := newTestPool(t, 0)
+		var workers sync.WaitGroup
+		for range 4 {
+			workers.Go(func() {
+				for range 100 {
+					p.add(peerID)
+					p.putOnCooldown(peerID)
+					p.cooldownLen()
+					p.remove(peerID)
+				}
+			})
+		}
+		workers.Wait()
+		p.remove(peerID)
+		p.releaseCooldown()
+		require.Zero(t, p.len())
+		require.Zero(t, p.cooldownLen())
+	})
 }
```

### share/shwap/p2p/shrex/peers/timedqueue.go
```diff
@@ -1,91 +1,83 @@
 package peers
 
 import (
-	"sync"
+	"slices"
 	"time"
 
 	"github.com/benbjohnson/clock"
 	"github.com/libp2p/go-libp2p/core/peer"
 )
 
-// timedQueue store items for ttl duration and releases it with calling onPop callback. Each item
-// is tracked independently
+// timedQueue stores items for ttl. The owner must hold its lock for all queue access,
+// including expiry from onTimer.
 type timedQueue struct {
-	sync.Mutex
-	items []item
-
-	// ttl is the amount of time each item exist in the timedQueue
-	ttl   time.Duration
-	clock clock.Clock
-	after *clock.Timer
-	// onPop will be called on item peer.ID after it is released
-	onPop func(peer.ID)
+	items   []item
+	ttl     time.Duration
+	clock   clock.Clock
+	after   *clock.Timer
+	onTimer func()
 }
 
 type item struct {
 	peer.ID
 	createdAt time.Time
 }
 
-func newTimedQueue(ttl time.Duration, onPop func(peer.ID)) *timedQueue {
+func newTimedQueue(ttl time.Duration, onTimer func()) *timedQueue {
 	return &timedQueue{
-		items: make([]item, 0),
-		clock: clock.New(),
-		ttl:   ttl,
-		onPop: onPop,
+		items:   make([]item, 0),
+		clock:   clock.New(),
+		ttl:     ttl,
+		onTimer: onTimer,
 	}
 }
 
-// releaseExpired will release all expired items
-func (q *timedQueue) releaseExpired() {
-	q.Lock()
-	defer q.Unlock()
-	q.releaseUnsafe()
-}
-
-func (q *timedQueue) releaseUnsafe() {
-	if len(q.items) == 0 {
-		return
-	}
-
-	var i int
+// releaseExpired removes expired items and calls onPop under the owner's lock.
+func (q *timedQueue) releaseExpired(onPop func(peer.ID)) {
+	n := 0
 	for _, next := range q.items {
-		timeIn := q.clock.Since(next.createdAt)
-		if timeIn < q.ttl {
-			// item is not expired yet, create a timer that will call releaseExpired
-			q.after.Stop()
-			q.after = q.clock.AfterFunc(q.ttl-timeIn, q.releaseExpired)
+		if q.clock.Since(next.createdAt) < q.ttl {
 			break
 		}
-
-		// item is expired
-		q.onPop(next.ID)
-		i++
-	}
-
-	if i > 0 {
-		copy(q.items, q.items[i:])
-		q.items = q.items[:len(q.items)-i]
+		onPop(next.ID)
+		n++
 	}
+	q.items = slices.Delete(q.items, 0, n)
+	q.schedule()
 }
 
 func (q *timedQueue) push(peerID peer.ID) {
-	q.Lock()
-	defer q.Unlock()
-
 	q.items = append(q.items, item{
 		ID:        peerID,
 		createdAt: q.clock.Now(),
 	})
-
-	// if it is the first item in queue, create a timer to call releaseExpired after its expiration
 	if len(q.items) == 1 {
-		q.after = q.clock.AfterFunc(q.ttl, q.releaseExpired)
+		q.schedule()
+	}
+}
+
+func (q *timedQueue) remove(peerID peer.ID) {
+	for i, entry := range q.items {
+		if entry.ID == peerID {
+			q.items = slices.Delete(q.items, i, i+1)
+			if i == 0 {
+				q.schedule()
+			}
+			return
+		}
+	}
+}
+
+func (q *timedQueue) schedule() {
+	if q.after != nil {
+		q.after.Stop()
+		q.after = nil
+	}
+	if len(q.items) > 0 {
+		q.after = q.clock.AfterFunc(q.ttl-q.clock.Since(q.items[0].createdAt), q.onTimer)
 	}
 }
 
 func (q *timedQueue) len() int {
-	q.Lock()
-	defer q.Unlock()
 	return len(q.items)
 }
```

### share/shwap/p2p/shrex/peers/timedqueue_test.go
```diff
@@ -10,51 +10,67 @@ import (
 )
 
 func TestTimedQueue(t *testing.T) {
-	t.Run("push item", func(t *testing.T) {
-		peers := []peer.ID{"peer1", "peer2"}
-		ttl := time.Second
+	const peer1, peer2 = "peer1", "peer2"
+	for _, remove := range []peer.ID{"", peer1, peer2, "missing"} {
+		t.Run("remove "+string(remove), func(t *testing.T) {
+			mock := clock.NewMock()
+			fired := make(chan struct{}, 2)
+			queue := newTimedQueue(time.Second, func() { fired <- struct{}{} })
+			queue.clock = mock
+			var popped []peer.ID
+			onPop := func(id peer.ID) { popped = append(popped, id) }
+			queue.releaseExpired(onPop)
+			require.Zero(t, queue.len())
 
-		popCh := make(chan struct{}, 1)
-		queue := newTimedQueue(ttl, func(id peer.ID) {
-			go func() {
-				require.Contains(t, peers, id)
-				popCh <- struct{}{}
-			}()
-		})
-		mock := clock.NewMock()
-		queue.clock = mock
-
-		// push first item | global time : 0
-		queue.push(peers[0])
-		require.Equal(t, queue.len(), 1)
+			queue.push(peer1)
+			mock.Add(time.Second / 2)
+			queue.push(peer2)
+			timer := queue.after
+			queue.remove(remove)
+			if remove == peer1 {
+				require.NotSame(t, timer, queue.after)
+			} else {
+				require.Same(t, timer, queue.after)
+			}
+			mock.Add(time.Second/2 - 1)
+			queue.releaseExpired(onPop)
+			require.Empty(t, popped)
+			require.Empty(t, fired)
 
-		// push second item with ttl/2 gap | global time : ttl/2
-		mock.Add(ttl / 2)
-		queue.push(peers[1])
-		require.Equal(t, queue.len(), 2)
+			mock.Add(1)
+			if remove == peer1 {
+				require.Empty(t, fired)
+			} else {
+				require.Len(t, fired, 1)
+				<-fired
+				queue.releaseExpired(onPop)
+				require.Equal(t, []peer.ID{peer1}, popped)
+			}
 
-		// advance clock 1 nano sec before first item should expire | global time : ttl - 1
-		mock.Add(ttl/2 - 1)
-		// check that releaseExpired doesn't remove items
-		queue.releaseExpired()
-		require.Equal(t, queue.len(), 2)
-		// first item should be released after its own timeout | global time : ttl
-		mock.Add(1)
-
-		select {
-		case <-popCh:
-		case <-time.After(ttl):
-			t.Fatal("first item is not released")
-		}
-		require.Equal(t, queue.len(), 1)
+			mock.Add(time.Second / 2)
+			if remove == peer2 {
+				require.Empty(t, fired)
+			} else {
+				require.Len(t, fired, 1)
+				<-fired
+				queue.releaseExpired(onPop)
+				require.Equal(t, peer.ID(peer2), popped[len(popped)-1])
+			}
+			require.Zero(t, queue.len())
+			require.Nil(t, queue.after)
+		})
+	}
 
-		// first item should be released after ttl/2 gap timeout | global time : 3/2*ttl
-		mock.Add(ttl / 2)
-		select {
-		case <-popCh:
-		case <-time.After(ttl):
-			t.Fatal("second item is not released")
-		}
-		require.Equal(t, queue.len(), 0)
+	t.Run("remove last entry stops timer", func(t *testing.T) {
+		mock := clock.NewMock()
+		fired := make(chan struct{}, 1)
+		queue := newTimedQueue(time.Second, func() { fired <- struct{}{} })
+		queue.clock = mock
+		queue.push(peer1)
+		queue.remove(peer1)
+		require.Zero(t, queue.len())
+		require.Nil(t, queue.after)
+		mock.Add(time.Second)
+		require.Empty(t, fired)
 	})
 }
```
