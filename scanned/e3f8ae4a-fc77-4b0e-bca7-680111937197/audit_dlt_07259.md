# [?] fix non deterministic test failures and race in privval socket (#3258)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2019-02-06
Source: https://github.com/cometbft/cometbft/commit/45b70ae031f18bb5b95794205785bd90e36ccd4b
Type: security-commit

## Details
fix non deterministic test failures and race in privval socket (#3258)

* node: decrease retry conn timeout in test

Should fix #3256

The retry timeout was set to the default, which is the same as the
accept timeout, so it's no wonder this would fail. Here we decrease the
retry timeout so we can try many times before the accept timeout.

* p2p: increase handshake timeout in test

This fails sometimes, presumably because the handshake timeout is so low
(only 50ms). So increase it to 1s. Should fix #3187

* privval: fix race with ping. closes #3237

Pings happen in a go-routine and can happen concurrently with other
messages. Since we use a request/response protocol, we expect to send a
request and get back the corresponding response. But with pings
happening concurrently, this assumption could be violated. We were using
a mutex, but only a RWMutex, where the RLock was being held for sending
messages - this was to allow the underlying connection to be replaced if
it fails. Turns out we actually need to use a full lock (not just a read
lock) to prevent multiple requests from happening concurrently.

* node: fix test name. DelayedStop -> DelayedStart

* autofile: Wait() method

In the TestWALTruncate in consensus/wal_test.go we remove the WAL
directory at the end of the test. However the wal.Stop() does not
properly wait for the autofile group to finish shutting down. Hence it
was possible that the group's go-routine is still running when the
cleanup happens, which causes a panic since the directory disappeared.
Here we add a Wait() method to properly wait until the go-routine exits
so we can safely clean up. This fixes #2852.

## Patch
### consensus/wal.go
```diff
@@ -112,11 +112,20 @@ func (wal *baseWAL) OnStart() error {
 	return err
 }
 
+// Stop the underlying autofile group.
+// Use Wait() to ensure it's finished shutting down
+// before cleaning up files.
 func (wal *baseWAL) OnStop() {
 	wal.group.Stop()
 	wal.group.Close()
 }
 
+// Wait for the underlying autofile group to finish shutting down
+// so it's safe to cleanup files.
+func (wal *baseWAL) Wait() {
+	wal.group.Wait()
+}
+
 // Write is called in newStep and for each receive on the
 // peerMsgQueue and the timeoutTicker.
 // NOTE: does not call fsync()
```

### consensus/wal_test.go
```diff
@@ -39,7 +39,12 @@ func TestWALTruncate(t *testing.T) {
 	wal.SetLogger(log.TestingLogger())
 	err = wal.Start()
 	require.NoError(t, err)
-	defer wal.Stop()
+	defer func() {
+		wal.Stop()
+		// wait for the wal to finish shutting down so we
+		// can safely remove the directory
+		wal.Wait()
+	}()
 
 	//60 block's size nearly 70K, greater than group's headBuf size(4096 * 10), when headBuf is full, truncate content will Flush to the file.
 	//at this time, RotateFile is called, truncate content exist in each file.
```

### libs/autofile/group.go
```diff
@@ -67,6 +67,11 @@ type Group struct {
 	minIndex           int // Includes head
 	maxIndex           int // Includes head, where Head will move to
 
+	// close this when the processTicks routine is done.
+	// this ensures we can cleanup the dir after calling Stop
+	// and the routine won't be trying to access it anymore
+	doneProcessTicks chan struct{}
+
 	// TODO: When we start deleting files, we need to start tracking GroupReaders
 	// and their dependencies.
 }
@@ -90,6 +95,7 @@ func OpenGroup(headPath string, groupOptions ...func(*Group)) (g *Group, err err
 		groupCheckDuration: defaultGroupCheckDuration,
 		minIndex:           0,
 		maxIndex:           0,
+		doneProcessTicks:   make(chan struct{}),
 	}
 
 	for _, option := range groupOptions {
@@ -140,6 +146,11 @@ func (g *Group) OnStop() {
 	g.Flush() // flush any uncommitted data
 }
 
+func (g *Group) Wait() {
+	// wait for processTicks routine to finish
+	<-g.doneProcessTicks
+}
+
 // Close closes the head file. The group must be stopped by this moment.
 func (g *Group) Close() {
 	g.Flush() // flush any uncommitted data
@@ -211,6 +222,7 @@ func (g *Group) Flush() error {
 }
 
 func (g *Group) processTicks() {
+	defer close(g.doneProcessTicks)
 	for {
 		select {
 		case <-g.ticker.C:
```

### node/node_test.go
```diff
@@ -88,13 +88,13 @@ func TestSplitAndTrimEmpty(t *testing.T) {
 	}
 }
 
-func TestNodeDelayedStop(t *testing.T) {
-	config := cfg.ResetTestRoot("node_delayed_node_test")
+func TestNodeDelayedStart(t *testing.T) {
+	config := cfg.ResetTestRoot("node_delayed_start_test")
 	now := tmtime.Now()
 
 	// create & start node
 	n, err := DefaultNewNode(config, log.TestingLogger())
-	n.GenesisDoc().GenesisTime = now.Add(5 * time.Second)
+	n.GenesisDoc().GenesisTime = now.Add(2 * time.Second)
 	require.NoError(t, err)
 
 	n.Start()
@@ -133,6 +133,7 @@ func TestNodeSetPrivValTCP(t *testing.T) {
 		types.NewMockPV(),
 		dialer,
 	)
+	privval.RemoteSignerConnDeadline(100 * time.Millisecond)(pvsc)
 
 	go func() {
 		err := pvsc.Start()
@@ -172,20 +173,18 @@ func TestNodeSetPrivValIPC(t *testing.T) {
 		types.NewMockPV(),
 		dialer,
 	)
+	privval.RemoteSignerConnDeadline(100 * time.Millisecond)(pvsc)
 
-	done := make(chan struct{})
 	go func() {
-		defer close(done)
-		n, err := DefaultNewNode(config, log.TestingLogger())
+		err := pvsc.Start()
 		require.NoError(t, err)
-		assert.IsType(t, &privval.SocketVal{}, n.PrivValidator())
 	}()
+	defer pvsc.Stop()
 
-	err := pvsc.Start()
+	n, err := DefaultNewNode(config, log.TestingLogger())
 	require.NoError(t, err)
-	defer pvsc.Stop()
+	assert.IsType(t, &privval.SocketVal{}, n.PrivValidator())
 
-	<-done
 }
 
 // testFreeAddr claims a free port so we don't block on listener being ready.
```

### p2p/test_util.go
```diff
@@ -125,7 +125,7 @@ func (sw *Switch) addPeerWithConnection(conn net.Conn) error {
 		return err
 	}
 
-	ni, err := handshake(conn, 50*time.Millisecond, sw.nodeInfo)
+	ni, err := handshake(conn, time.Second, sw.nodeInfo)
 	if err != nil {
 		if err := conn.Close(); err != nil {
 			sw.Logger.Error("Error closing connection", "err", err)
```

### privval/client.go
```diff
@@ -53,9 +53,11 @@ type SocketVal struct {
 	// reset if the connection fails.
 	// failures are detected by a background
 	// ping routine.
+	// All messages are request/response, so we hold the mutex
+	// so only one request/response pair can happen at a time.
 	// Methods on the underlying net.Conn itself
 	// are already gorountine safe.
-	mtx    sync.RWMutex
+	mtx    sync.Mutex
 	signer *RemoteSignerClient
 }
 
@@ -82,22 +84,22 @@ func NewSocketVal(
 
 // GetPubKey implements PrivValidator.
 func (sc *SocketVal) GetPubKey() crypto.PubKey {
-	sc.mtx.RLock()
-	defer sc.mtx.RUnlock()
+	sc.mtx.Lock()
+	defer sc.mtx.Unlock()
 	return sc.signer.GetPubKey()
 }
 
 // SignVote implements PrivValidator.
 func (sc *SocketVal) SignVote(chainID string, vote *types.Vote) error {
-	sc.mtx.RLock()
-	defer sc.mtx.RUnlock()
+	sc.mtx.Lock()
+	defer sc.mtx.Unlock()
 	return sc.signer.SignVote(chainID, vote)
 }
 
 // SignProposal implements PrivValidator.
 func (sc *SocketVal) SignProposal(chainID string, proposal *types.Proposal) error {
-	sc.mtx.RLock()
-	defer sc.mtx.RUnlock()
+	sc.mtx.Lock()
+	defer sc.mtx.Unlock()
 	return sc.signer.SignProposal(chainID, proposal)
 }
 
@@ -106,15 +108,15 @@ func (sc *SocketVal) SignProposal(chainID string, proposal *types.Proposal) erro
 
 // Ping is used to check connection health.
 func (sc *SocketVal) Ping() error {
-	sc.mtx.RLock()
-	defer sc.mtx.RUnlock()
+	sc.mtx.Lock()
+	defer sc.mtx.Unlock()
 	return sc.signer.Ping()
 }
 
 // Close closes the underlying net.Conn.
 func (sc *SocketVal) Close() {
-	sc.mtx.RLock()
-	defer sc.mtx.RUnlock()
+	sc.mtx.Lock()
+	defer sc.mtx.Unlock()
 	if sc.signer != nil {
 		if err := sc.signer.Close(); err != nil {
 			sc.Logger.Error("OnStop", "err", err)
```
