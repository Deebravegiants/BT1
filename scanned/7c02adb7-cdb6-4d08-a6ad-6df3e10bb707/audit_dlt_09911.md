# [?] Merge pull request #944 from kaiachain/fix/istanbul-newchainhead-deadlock

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2026-06-22
Source: https://github.com/kaiachain/kaia/commit/8cf7d8f2e186ecd76167969aa1569da71960743a
Type: security-commit

## Details
Merge pull request #944 from kaiachain/fix/istanbul-newchainhead-deadlock

consensus: break Start/NewChainHead deadlock on coreMu

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
