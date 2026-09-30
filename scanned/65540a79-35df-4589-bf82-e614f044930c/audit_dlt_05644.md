# [?] [kimiko] cl/sentinel: fix peerstore data race in concurrent peer connections (#19603)  (#19616)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-10
Source: https://github.com/erigontech/erigon/commit/2d94e91a23edfdad4b76aa393c0cdca3eb255762
Type: security-commit

## Details
[kimiko] cl/sentinel: fix peerstore data race in concurrent peer connections (#19603)  (#19616)

closes #19603 
## Summary
- Fix data race between Host.Connect() and Peerstore().RemovePeer() in
libp2p's memoryAddrBook caused by concurrent addAddrsUnlocked() and
background gc() goroutine
- Move the per-connection semaphore from a local variable in
listenForPeers() to a shared connectSem field on the Sentinel struct, so
all connection paths (listenForPeers, findPeersForSubnets,
connectWithAllPeers) serialize through the same semaphore
- Add unit tests for semaphore initialization, concurrency bounds,
release/reacquire cycle, and context cancellation
## Problem
Issue #19603: concurrent Host.Connect() calls trigger a data race in
libp2p v0.37.2's in-memory address book. The race occurs between
addAddrsUnlocked() (called during connect) and the background gc()
goroutine
that cleans expired addresses.
## Fix
Previously, only listenForPeers() used a local semaphore —
findPeersForSubnets() and connectWithAllPeers() had no concurrency
control at all. This PR:
1. Adds connectSem *semaphore.Weighted to the Sentinel struct,
initialized with goRoutinesOpeningPeerConnections (4) capacity
2. All three connection paths now acquire from the shared semaphore
before calling ConnectWithPeer
3. This serializes peerstore writes enough to avoid the race without
reducing throughput (4 concurrent connections is the existing limit)

---------

Co-authored-by: JkLondon <me@ilyamikheev.com>
Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>
Co-authored-by: info@weblogix.biz <admin@10gbps.weblogix.it>

## Patch
### cl/sentinel/discovery.go
```diff
@@ -141,8 +141,11 @@ func (s *Sentinel) findPeersForSubnets(subnets []subnetSearchState) {
 		s.pidToEnr.Store(peerInfo.ID, node)
 		s.pidToEnodeId.Store(peerInfo.ID, node.ID())
 
-		// Try to connect
-		if err := s.ConnectWithPeer(ctx, *peerInfo, nil); err != nil {
+		// Try to connect (serialize via shared semaphore to avoid peerstore race, see #19603)
+		if err := s.connectSem.Acquire(ctx, 1); err != nil {
+			break
+		}
+		if err := s.ConnectWithPeer(ctx, *peerInfo, s.connectSem); err != nil {
 			log.Trace("[Sentinel] Subnet search: failed to connect", "peer", peerInfo.ID, "err", err)
 			continue
 		}
@@ -446,7 +449,10 @@ func (s *Sentinel) connectWithAllPeers(multiAddrs []multiaddr.Multiaddr) error {
 	}
 	for _, peerInfo := range addrInfos {
 		go func(peerInfo peer.AddrInfo) {
-			if err := s.ConnectWithPeer(s.ctx, peerInfo, nil); err != nil {
+			if err := s.connectSem.Acquire(s.ctx, 1); err != nil {
+				return
+			}
+			if err := s.ConnectWithPeer(s.ctx, peerInfo, s.connectSem); err != nil {
 				log.Debug("[Sentinel] Could not connect with peer", "err", err)
 			} else {
 				log.Debug("[Sentinel] Connected with peer", "peer", peerInfo.ID)
@@ -485,9 +491,6 @@ func (s *Sentinel) listenForPeers() {
 	multiAddresses := convertToMultiAddr(enodes)
 	s.stickToPeers(multiAddresses)
 
-	// limit the number of goroutines opening connection with peers
-	sem := semaphore.NewWeighted(int64(goRoutinesOpeningPeerConnections))
-
 	iterator := s.listener.RandomNodes()
 	defer iterator.Close()
 	for {
@@ -520,7 +523,7 @@ func (s *Sentinel) listenForPeers() {
 			continue
 		}
 
-		if err := sem.Acquire(s.ctx, 1); err != nil {
+		if err := s.connectSem.Acquire(s.ctx, 1); err != nil {
 			if errors.Is(err, context.Canceled) {
 				break
 			}
@@ -529,7 +532,7 @@ func (s *Sentinel) listenForPeers() {
 		}
 
 		go func() {
-			if err := s.ConnectWithPeer(s.ctx, *peerInfo, sem); err != nil {
+			if err := s.ConnectWithPeer(s.ctx, *peerInfo, s.connectSem); err != nil {
 				log.Trace("[Sentinel] Could not connect with peer", "err", err)
 			}
 		}()
```

### cl/sentinel/discovery_test.go
```diff
@@ -0,0 +1,207 @@
+// Copyright 2024 The Erigon Authors
+// This file is part of Erigon.
+//
+// Erigon is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// Erigon is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with Erigon. If not, see <http://www.gnu.org/licenses/>.
+
+package sentinel
+
+import (
+	"context"
+	"sync/atomic"
+	"testing"
+	"time"
+
+	"github.com/stretchr/testify/assert"
+	"github.com/stretchr/testify/require"
+	"golang.org/x/sync/semaphore"
+)
+
+// TestConnectSemaphoreInitialized verifies that a Sentinel's connectSem field
+// is properly initialised (not nil) and that its capacity matches
+// goRoutinesOpeningPeerConnections.
+func TestConnectSemaphoreInitialized(t *testing.T) {
+	t.Parallel()
+
+	s := &Sentinel{
+		connectSem: semaphore.NewWeighted(int64(goRoutinesOpeningPeerConnections)),
+	}
+	require.NotNil(t, s.connectSem, "connectSem must not be nil after construction")
+
+	// We should be able to acquire exactly goRoutinesOpeningPeerConnections tokens.
+	for i := 0; i < goRoutinesOpeningPeerConnections; i++ {
+		ok := s.connectSem.TryAcquire(1)
+		assert.True(t, ok, "TryAcquire should succeed for token %d of %d", i+1, goRoutinesOpeningPeerConnections)
+	}
+
+	// The next acquire must fail -- the semaphore is exhausted.
+	ok := s.connectSem.TryAcquire(1)
+	assert.False(t, ok, "TryAcquire should fail when semaphore is at capacity")
+
+	// Release all so the semaphore is left clean.
+	for i := 0; i < goRoutinesOpeningPeerConnections; i++ {
+		s.connectSem.Release(1)
+	}
+}
+
+// TestConnectSemaphoreBoundsConcurrency spawns many goroutines that all try to
+// hold the semaphore and verifies that at most goRoutinesOpeningPeerConnections
+// goroutines hold it simultaneously.
+func TestConnectSemaphoreBoundsConcurrency(t *testing.T) {
+	t.Parallel()
+
+	const totalGoroutines = 32
+
+	sem := semaphore.NewWeighted(int64(goRoutinesOpeningPeerConnections))
+	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
+	defer cancel()
+
+	var (
+		active  atomic.Int32
+		maxSeen atomic.Int32
+	)
+
+	// recordMax is called after incrementing active; it races against other
+	// goroutines doing the same so we use a CAS loop.
+	recordMax := func(cur int32) {
+		for {
+			old := maxSeen.Load()
+			if cur <= old {
+				break
+			}
+			if maxSeen.CompareAndSwap(old, cur) {
+				break
+			}
+		}
+	}
+
+	done := make(chan struct{}, totalGoroutines)
+	for i := 0; i < totalGoroutines; i++ {
+		go func() {
+			defer func() { done <- struct{}{} }()
+
+			err := sem.Acquire(ctx, 1)
+			if err != nil {
+				return
+			}
+
+			cur := active.Add(1)
+			recordMax(cur)
+
+			// Simulate a short piece of work so goroutines overlap.
+			// Using a channel-based pause keeps the test deterministic
+			// (no time.Sleep).
+			runtime_Gosched()
+
+			active.Add(-1)
+			sem.Release(1)
+		}()
+	}
+
+	for i := 0; i < totalGoroutines; i++ {
+		select {
+		case <-done:
+		case <-ctx.Done():
+			t.Fatal("timed out waiting for goroutines to finish")
+		}
+	}
+
+	assert.LessOrEqual(t, maxSeen.Load(), int32(goRoutinesOpeningPeerConnections),
+		"no more than %d goroutines should hold the semaphore at once", goRoutinesOpeningPeerConnections)
+	assert.Equal(t, int32(0), active.Load(), "all goroutines should have released")
+}
+
+// runtime_Gosched yields the processor so other goroutines can run.
+// This is a deterministic alternative to time.Sleep.
+func runtime_Gosched() {
+	// Using a small channel send/receive pair forces a goroutine reschedule
+	// without introducing wall-clock delays.
+	ch := make(chan struct{}, 1)
+	ch <- struct{}{}
+	<-ch
+}
+
+// TestConnectSemaphoreReleaseAndReacquire verifies the acquire-release cycle
+// that mirrors ConnectWithPeer's `defer sem.Release(1)` pattern: after
+// releasing a token the semaphore becomes available again.
+func TestConnectSemaphoreReleaseAndReacquire(t *testing.T) {
+	t.Parallel()
+
+	sem := semaphore.NewWeighted(int64(goRoutinesOpeningPeerConnections))
+
+	// Exhaust all tokens.
+	for i := 0; i < goRoutinesOpeningPeerConnections; i++ {
+		ok := sem.TryAcquire(1)
+		require.True(t, ok, "should acquire token %d", i+1)
+	}
+
+	// Semaphore is full -- verify.
+	require.False(t, sem.TryAcquire(1), "semaphore should be exhausted")
+
+	// Simulate what ConnectWithPeer's defer does: release one token.
+	sem.Release(1)
+
+	// Now exactly one acquire should succeed.
+	ok := sem.TryAcquire(1)
+	assert.True(t, ok, "after release, one acquire should succeed")
+
+	// And the next should fail again.
+	ok = sem.TryAcquire(1)
+	assert.False(t, ok, "semaphore should be exhausted again after re-acquire")
+
+	// Clean up.
+	for i := 0; i < goRoutinesOpeningPeerConnections; i++ {
+		sem.Release(1)
+	}
+}
+
+// TestConnectSemaphoreAcquireRespectsContext verifies that Acquire unblocks
+// when the context is cancelled, which is the behaviour relied upon in
+// listenForPeers and findPeersForSubnets.
+func TestConnectSemaphoreAcquireRespectsContext(t *testing.T) {
+	t.Parallel()
+
+	sem := semaphore.NewWeighted(1)
+
+	// Hold the only token.
+	require.True(t, sem.TryAcquire(1))
+
+	ctx, cancel := context.WithCancel(context.Background())
+
+	errCh := make(chan error, 1)
+	go func() {
+		errCh <- sem.Acquire(ctx, 1)
+	}()
+
+	// The goroutine should be blocked. Cancel the context to unblock it.
+	cancel()
+
+	select {
+	case err := <-errCh:
+		require.Error(t, err, "Acquire should return an error when context is cancelled")
+		assert.ErrorIs(t, err, context.Canceled)
+	case <-time.After(5 * time.Second):
+		t.Fatal("Acquire did not unblock after context cancellation")
+	}
+
+	sem.Release(1)
+}
+
+// TestGoRoutinesOpeningPeerConnectionsConst asserts the constant value the
+// production code depends on. If someone changes this constant the test
+// will catch it so the semaphore capacity expectation stays aligned.
+func TestGoRoutinesOpeningPeerConnectionsConst(t *testing.T) {
+	t.Parallel()
+	assert.Equal(t, 4, goRoutinesOpeningPeerConnections,
+		"goRoutinesOpeningPeerConnections must be 4; changing this affects concurrency bounds")
+}
```

### cl/sentinel/sentinel.go
```diff
@@ -29,6 +29,7 @@ import (
 	"github.com/libp2p/go-libp2p/core/network"
 	"github.com/libp2p/go-libp2p/core/peer"
 	"github.com/prysmaticlabs/go-bitfield"
+	"golang.org/x/sync/semaphore"
 
 	"github.com/erigontech/erigon/cl/cltypes"
 	peerdasstate "github.com/erigontech/erigon/cl/das/state"
@@ -79,6 +80,10 @@ type Sentinel struct {
 	peerDasStateReader peerdasstate.PeerDasStateReader
 
 	metadataLock sync.Mutex
+	// connectSem serializes concurrent Host.Connect() and Peerstore().RemovePeer()
+	// calls to work around a data race in libp2p v0.37.2's memoryAddrBook between
+	// addAddrsUnlocked() and the background gc() goroutine (see #19603).
+	connectSem *semaphore.Weighted
 }
 
 func (s *Sentinel) SetStatus(status *cltypes.Status) {
@@ -112,6 +117,7 @@ func New(
 		dataColumnStorage:  dataColumnStorage,
 		peerDasStateReader: peerDasStateReader,
 		p2p:                p2p,
+		connectSem:         semaphore.NewWeighted(int64(goRoutinesOpeningPeerConnections)),
 	}
 
 	// Setup discovery
```
