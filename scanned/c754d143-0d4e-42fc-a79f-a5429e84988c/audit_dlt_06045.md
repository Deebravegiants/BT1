# [?] fix(istanbul): break Start/NewChainHead deadlock on coreMu

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2026-06-17
Source: https://github.com/kaiachain/kaia/commit/e165330daaa8c29a45a486c46c0a90c6955a3d9a
Type: security-commit

## Details
fix(istanbul): break Start/NewChainHead deadlock on coreMu

backend.Start holds coreMu while core.Start synchronously posts a
NewSequenceEvent to the worker's event loop and waits for it to be consumed.
That same loop, when handling a ChainHeadEvent, calls backend.NewChainHead,
which took coreMu.RLock. When a node finishes syncing and resumes mining (the
sync->mine transition, with a freshly imported block's ChainHeadEvent still in
flight) the two collide: Start holds the write lock and waits for the worker,
while the worker is blocked acquiring the read lock -> permanent deadlock. All
later consensus message handling (HandleMsg) and even shutdown (Stop, which also
locks coreMu) then block, so the node freezes and can only be SIGKILLed.

NewChainHead only needs coreMu to read the coreStarted flag before an
already-asynchronous event post. Make coreStarted an atomic.Bool and read it
locklessly in NewChainHead so the worker loop never blocks on coreMu;
Start/Stop/HandleMsg keep their existing coreMu usage. This removes the
lock-vs-channel cycle without changing any consensus event timing. Pre-existing
issue (not permissionless-specific); it surfaced once nodes could actually catch
up via sync and reach the sync->mine transition.

Constraint: NewChainHead runs in the worker event loop and must never block on coreMu
Rejected: make the NewSequenceEvent post async | changes consensus event ordering
Rejected: drop coreMu across core.Start in backend.Start | widens the Start/Stop lifecycle race window
Confidence: high
Scope-risk: narrow
Directive: do not reintroduce coreMu (or any lock backend.Start holds) into NewChainHead
Not-tested: snap/fast-sync paths (reproduced and verified on the full-sync sync->mine transition)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

## Patch
### consensus/istanbul/backend/backend.go
```diff
@@ -69,7 +69,6 @@ func New(opts *BackendOpts) consensus.Engine {
 		logger:           logger.NewWith(),
 		commitCh:         make(chan *types.Result, 1),
 		candidates:       make(map[common.Address]bool),
-		coreStarted:      false,
 		recentMessages:   recentMessages,
 		knownMessages:    knownMessages,
 		sealer:           istanbul.NewSealerImpl(opts.PrivateKey),
@@ -98,7 +97,7 @@ type backend struct {
 	proposedBlockHash common.Hash
 	sealMu            sync.Mutex
 	sealSkippedNum    uint64 // block number that was committed before Seal started (0 = none)
-	coreStarted       bool
+	coreStarted       atomic.Bool
 	coreMu            sync.RWMutex
 
 	// Current list of candidates we are pushing
```

### consensus/istanbul/backend/engine.go
```diff
@@ -154,7 +154,7 @@ func (sb *backend) RegisterKaiaxModules(mGov gov.GovModule, mValset valset.Valse
 func (sb *backend) Start(chain consensus.ChainReader, executor consensus.Executor) error {
 	sb.coreMu.Lock()
 	defer sb.coreMu.Unlock()
-	if sb.coreStarted {
+	if sb.coreStarted.Load() {
 		return istanbul.ErrStartedEngine
 	}
 
@@ -183,7 +183,7 @@ func (sb *backend) Start(chain consensus.ChainReader, executor consensus.Executo
 		return err
 	}
 
-	sb.coreStarted = true
+	sb.coreStarted.Store(true)
 	return nil
 }
 
@@ -193,7 +193,7 @@ func (sb *backend) Stop() error {
 	defer sb.coreMu.Unlock()
 	// Unblock any peers waiting in ValidatePeerType during shutdown.
 	sb.SignalPeerRegistrable()
-	if !sb.coreStarted {
+	if !sb.coreStarted.Load() {
 		return istanbul.ErrStoppedEngine
 	}
 	// Close commitCh to stop any pending Seal() calls
@@ -207,7 +207,7 @@ func (sb *backend) Stop() error {
 	if err := sb.core.Stop(); err != nil {
 		return err
 	}
-	sb.coreStarted = false
+	sb.coreStarted.Store(false)
 	return nil
 }
 
```

### consensus/istanbul/backend/handler.go
```diff
@@ -54,7 +54,7 @@ func (sb *backend) HandleMsg(addr common.Address, msg p2p.Msg) (bool, error) {
 	defer sb.coreMu.Unlock()
 
 	if msg.Code == consensus.ConsensusMsgCode {
-		if !sb.coreStarted {
+		if !sb.coreStarted.Load() {
 			return true, istanbul.ErrStoppedEngine
 		}
 
@@ -138,9 +138,9 @@ func (sb *backend) SetBroadcaster(broadcaster consensus.Broadcaster) {
 }
 
 func (sb *backend) NewChainHead() error {
-	sb.coreMu.RLock()
-	defer sb.coreMu.RUnlock()
-	if !sb.coreStarted {
+	// Do not take coreMu here. NewChainHead runs on the worker loop, and a
+	// coreMu holder can block waiting on that loop, so locking risks a deadlock.
+	if !sb.coreStarted.Load() {
 		return istanbul.ErrStoppedEngine
 	}
 
```
