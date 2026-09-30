# [?] fix(op-supernode): resolve VirtualNode mutex deadlock during shutdown (#19680)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-03-20
Source: https://github.com/ethereum-optimism/optimism/commit/a33079410dc92678aa3cbde43111d9e26513ba10
Type: security-commit

## Details
fix(op-supernode): resolve VirtualNode mutex deadlock during shutdown (#19680)

VirtualNode.Start() held v.mu while calling inner.Stop(), but
inner.Stop() drains the op-node event system which calls back into
SyncStatus() — which also needs v.mu. This created a deadlock during
test cleanup, causing TestChallengerRespondsToMultipleInvalidClaimsEOA
to hang for 2 hours in CI.

Fix: release v.mu before calling inner.Stop(). State transitions
(VNStateStopped, clear cancel) happen under the lock, then the local
`n` variable (already holding the inner node reference) is used for
Stop() outside the lock. Also use `n` for the Start() goroutine
launch for consistency — never access v.inner outside v.mu.

Additionally, add a 60s defensive timeout to Supernode.Stop()'s
wg.Wait() so cleanup always proceeds in bounded time.

Refs: ethereum-optimism/optimism#19563

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### op-supernode/supernode/chain_container/virtual_node/virtual_node.go
```diff
@@ -128,32 +128,32 @@ func (v *simpleVirtualNode) Start(ctx context.Context) error {
 		return err
 	}
 	v.inner = n
-	// Release the lock once the inner node is created
 	v.state = VNStateRunning
 	v.mu.Unlock()
-	// Don't hold the lock while running or waiting for inner node to stop
 
 	// Run inner node in goroutine
 	// and await any signal to exit (Stop(), parent ctx, or inner error)
 	var innerErr error = nil
 	go func() {
-		innerErr = v.inner.Start(runCtx)
+		innerErr = n.Start(runCtx)
 	}()
 	<-runCtx.Done()
 
-	// Clean up with lock to end of function
+	// Update state under lock, but do NOT hold the lock during inner.Stop().
+	// inner.Stop() drains the op-node event system, which may call back into
+	// this VirtualNode (e.g. SyncStatus via EngineController.FinalizedHead).
+	// SyncStatus needs v.mu, so holding it here would deadlock.
 	v.mu.Lock()
-	defer v.mu.Unlock()
 	v.state = VNStateStopped
 	v.cancel = nil
+	v.mu.Unlock()
 
-	// Stop the inner node if it's still running
-	if v.inner != nil {
-		stopCtx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
-		defer cancel()
-		if err := v.inner.Stop(stopCtx); err != nil {
-			v.log.Error("error stopping inner node", "err", err)
-		}
+	// Stop the inner node outside the lock. Use n which is the local reference
+	// to the inner node created at the top of this function.
+	stopCtx, stopCancel := context.WithTimeout(context.Background(), 30*time.Second)
+	defer stopCancel()
+	if err := n.Stop(stopCtx); err != nil {
+		v.log.Error("error stopping inner node", "err", err)
 	}
 
 	// Return inner error if that's what caused the cancellation, otherwise context error
```

### op-supernode/supernode/chain_container/virtual_node/virtual_node_test.go
```diff
@@ -546,3 +546,100 @@ func TestVirtualNode_L1AtSafeHead(t *testing.T) {
 		require.ErrorIs(t, err, ErrL1AtSafeHeadNotFound)
 	})
 }
+
+// blockingStopMock wraps mockInnerNode but blocks Stop() until explicitly released.
+// This simulates an OpNode whose shutdown (event drain) takes a long time.
+type blockingStopMock struct {
+	*mockInnerNode
+	stopStarted chan struct{}
+	stopRelease chan struct{}
+}
+
+func (m *blockingStopMock) Stop(ctx context.Context) error {
+	close(m.stopStarted)
+	select {
+	case <-m.stopRelease:
+	case <-ctx.Done():
+		return ctx.Err()
+	}
+	return m.stopErr
+}
+
+// TestVirtualNode_SyncStatusDuringShutdown proves that SyncStatus does not deadlock
+// when called while Start() is shutting down the inner node. Before the fix,
+// Start() held v.mu during inner.Stop(), so any concurrent SyncStatus() call
+// would block on v.mu forever — creating a deadlock if the inner node's shutdown
+// path called back into SyncStatus (e.g. via the event system).
+func TestVirtualNode_SyncStatusDuringShutdown(t *testing.T) {
+	t.Parallel()
+	log := createTestLogger()
+	cfg := createTestConfig()
+	initOverload := &rollupNode.InitializationOverrides{}
+
+	mock := newMockInnerNode()
+	mock.startFunc = func(ctx context.Context) {
+		<-ctx.Done()
+	}
+	mock.stopCh = nil // prevent close in default Stop — we use blockingStopMock
+
+	stopStarted := make(chan struct{})
+	stopRelease := make(chan struct{})
+	blocking := &blockingStopMock{
+		mockInnerNode: mock,
+		stopStarted:   stopStarted,
+		stopRelease:   stopRelease,
+	}
+
+	vn := NewVirtualNode(cfg, log, initOverload, "test")
+	vn.innerNodeFactory = func(ctx context.Context, cfg *opnodecfg.Config,
+		log gethlog.Logger, appVersion string, m *opmetrics.Metrics,
+		initOverload *rollupNode.InitializationOverrides) (innerNode, error) {
+		return blocking, nil
+	}
+
+	ctx, cancel := context.WithCancel(context.Background())
+	startDone := make(chan error, 1)
+	go func() {
+		startDone <- vn.Start(ctx)
+	}()
+
+	// Wait for running
+	require.Eventually(t, func() bool {
+		return vn.State() == VNStateRunning
+	}, time.Second, 10*time.Millisecond)
+
+	// Cancel to trigger shutdown — Start() will call inner.Stop() which blocks
+	cancel()
+
+	// Wait for inner.Stop() to be entered
+	select {
+	case <-stopStarted:
+	case <-time.After(5 * time.Second):
+		t.Fatal("inner.Stop() was never called")
+	}
+
+	// Now try to call SyncStatus — this MUST NOT deadlock.
+	// Before the fix, this would block forever on v.mu.
+	syncDone := make(chan struct{})
+	go func() {
+		_, _ = vn.SyncStatus(context.Background())
+		close(syncDone)
+	}()
+
+	select {
+	case <-syncDone:
+		// Success — SyncStatus completed without deadlock
+	case <-time.After(5 * time.Second):
+		t.Fatal("SyncStatus deadlocked during shutdown — v.mu held during inner.Stop()")
+	}
+
+	// Release inner.Stop() so Start() can return
+	close(stopRelease)
+
+	select {
+	case <-startDone:
+		require.Equal(t, VNStateStopped, vn.State())
+	case <-time.After(5 * time.Second):
+		t.Fatal("Start() did not return after inner.Stop() completed")
+	}
+}
```

### op-supernode/supernode/supernode.go
```diff
@@ -261,8 +261,17 @@ func (s *Supernode) Stop(ctx context.Context) error {
 	}
 
 	s.log.Info("all chain containers stopped, waiting for goroutines to finish")
-	s.wg.Wait()
-	s.log.Info("goroutines finished, closing l1 client")
+	wgDone := make(chan struct{})
+	go func() {
+		s.wg.Wait()
+		close(wgDone)
+	}()
+	select {
+	case <-wgDone:
+		s.log.Info("goroutines finished, closing l1 client")
+	case <-time.After(60 * time.Second):
+		s.log.Error("timed out waiting for chain goroutines to finish after 60s, proceeding with cleanup")
+	}
 
 	if s.l1Client != nil {
 		s.l1Client.Close()
```
