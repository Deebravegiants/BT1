# [?] Fix deadlock on engine start (#1685)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-09-24
Source: https://github.com/celo-org/celo-blockchain/commit/00a9a9d191becec1ca922490674efbfeac3101a8
Type: security-commit

## Details
Fix deadlock on engine start (#1685)

* Fix deadlock during StartValidating

StartValidating makes a call to RefreshValPeers while holding
coreMu and RefreshValPeers waits for all validator peers to be deleted
and then reconnects to known validators.

If any of those peers has called IsValidating before RefreshValPeers
tries to delete them, the system gets stuck in a deadlock because
IsValidating also tries to acquire coreMu. The peer will never acquire
coreMu because it is held by StartValidating, and StartValidating will
never return because it is waiting for all peers to disconnect.

This commit makes coreStarted into an atomic variable so that peers can
make threadsafe calls to IsValidating without needing to acquire
coreStarted.

* Fix long wait for nodes to connect

At test startup sometimes nodes were taking in the region of 30s to connect
whilst other times it was happening in μs. The problem was we were
trying to connect all peers to all other peers. That meant that for any
two peers they would both dial each other. Sometimes if this occurred
close enough in time both sides would hang up the connections (I call
this cross dialing). This happens because each side counts their
outgoing connection as connected and then when the incoming connection
arrives they drop it because they see themselves as already connected.
When this happened nodes would retry after some time probably 30s and
then be connected.

The fix was to ensure that for any two nodes only one of them dials the
other.

## Patch
### consensus/istanbul/backend/api.go
```diff
@@ -193,7 +193,7 @@ func (api *API) GetCurrentRoundState() (*core.RoundStateSummary, error) {
 	api.istanbul.coreMu.RLock()
 	defer api.istanbul.coreMu.RUnlock()
 
-	if !api.istanbul.coreStarted {
+	if !api.istanbul.isCoreStarted() {
 		return nil, istanbul.ErrStoppedEngine
 	}
 	return api.istanbul.core.CurrentRoundState().Summary(), nil
@@ -203,7 +203,7 @@ func (api *API) ForceRoundChange() (bool, error) {
 	api.istanbul.coreMu.RLock()
 	defer api.istanbul.coreMu.RUnlock()
 
-	if !api.istanbul.coreStarted {
+	if !api.istanbul.isCoreStarted() {
 		return false, istanbul.ErrStoppedEngine
 	}
 	api.istanbul.core.ForceRoundChange()
```

### consensus/istanbul/backend/backend.go
```diff
@@ -113,13 +113,15 @@ func New(config *istanbul.Config, db ethdb.Database) consensus.Istanbul {
 		logger.Crit("Failed to create recent snapshots cache", "err", err)
 	}
 
+	coreStarted := atomic.Value{}
+	coreStarted.Store(false)
 	backend := &Backend{
 		config:                             config,
 		istanbulEventMux:                   new(event.TypeMux),
 		logger:                             logger,
 		db:                                 db,
 		recentSnapshots:                    recentSnapshots,
-		coreStarted:                        false,
+		coreStarted:                        coreStarted,
 		announceRunning:                    false,
 		gossipCache:                        NewLRUGossipCache(inmemoryPeers, inmemoryMessages),
 		announceThreadWg:                   new(sync.WaitGroup),
@@ -221,7 +223,16 @@ type Backend struct {
 	validateState       func(block *types.Block, statedb *state.StateDB, receipts types.Receipts, usedGas uint64) error
 	onNewConsensusBlock func(block *types.Block, receipts []*types.Receipt, logs []*types.Log, state *state.StateDB)
 
-	coreStarted bool
+	// We need this to be an atomic value so that we can access it in a lock
+	// free way from IsValidating. This is required because StartValidating
+	// makes a call to RefreshValPeers while holding coreMu and RefreshValPeers
+	// waits for all validator peers to be deleted and then reconnects to known
+	// validators. If any of those peers has called IsValidating before
+	// RefreshValPeers tries to delete them the system gets stuck in a
+	// deadlock, the peer will never acquire coreMu because it is held by
+	// StartValidating, and StartValidating will never return because it is
+	// waiting for all peers to disconnect.
+	coreStarted atomic.Value
 	coreMu      sync.RWMutex
 
 	// Snapshots for recent blocks to speed up reorgs
@@ -325,6 +336,10 @@ type Backend struct {
 	abortCommitHook func(result *istanbulCore.StateProcessResult) bool // Method to call upon committing a proposal
 }
 
+func (sb *Backend) isCoreStarted() bool {
+	return sb.coreStarted.Load().(bool)
+}
+
 // IsProxy returns true if instance has proxy flag
 func (sb *Backend) IsProxy() bool {
 	return sb.config.Proxy
@@ -350,9 +365,7 @@ func (sb *Backend) GetProxiedValidatorEngine() proxy.ProxiedValidatorEngine {
 // IsValidating return true if instance is validating
 func (sb *Backend) IsValidating() bool {
 	// TODO: Maybe a little laggy, but primary / replica should track the core
-	sb.coreMu.RLock()
-	defer sb.coreMu.RUnlock()
-	return sb.coreStarted
+	return sb.isCoreStarted()
 }
 
 // IsValidator return if instance is a validator (either proxied or standalone)
```

### consensus/istanbul/backend/engine.go
```diff
@@ -630,7 +630,7 @@ func (sb *Backend) updateReplicaStateLoop(bc *ethCore.BlockChain) {
 		select {
 		case chainEvent := <-chainEventCh:
 			sb.coreMu.RLock()
-			if !sb.coreStarted && sb.replicaState != nil {
+			if !sb.isCoreStarted() && sb.replicaState != nil {
 				consensusBlock := new(big.Int).Add(chainEvent.Block.Number(), common.Big1)
 				sb.replicaState.NewChainHead(consensusBlock)
 			}
@@ -649,7 +649,7 @@ func (sb *Backend) SetCallBacks(hasBadBlock func(common.Hash) bool,
 	onNewConsensusBlock func(block *types.Block, receipts []*types.Receipt, logs []*types.Log, state *state.StateDB)) error {
 	sb.coreMu.RLock()
 	defer sb.coreMu.RUnlock()
-	if sb.coreStarted {
+	if sb.isCoreStarted() {
 		return istanbul.ErrStartedEngine
 	}
 
@@ -664,7 +664,7 @@ func (sb *Backend) SetCallBacks(hasBadBlock func(common.Hash) bool,
 func (sb *Backend) StartValidating() error {
 	sb.coreMu.Lock()
 	defer sb.coreMu.Unlock()
-	if sb.coreStarted {
+	if sb.isCoreStarted() {
 		return istanbul.ErrStartedEngine
 	}
 
@@ -684,7 +684,7 @@ func (sb *Backend) StartValidating() error {
 		sb.UpdateAnnounceVersion()
 	}
 
-	sb.coreStarted = true
+	sb.coreStarted.Store(true)
 
 	// coreStarted must be true by this point for validator peers to be successfully added
 	if !sb.config.Proxied {
@@ -700,14 +700,14 @@ func (sb *Backend) StartValidating() error {
 func (sb *Backend) StopValidating() error {
 	sb.coreMu.Lock()
 	defer sb.coreMu.Unlock()
-	if !sb.coreStarted {
+	if !sb.isCoreStarted() {
 		return istanbul.ErrStoppedEngine
 	}
 	sb.logger.Info("Stopping istanbul.Engine validating")
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
@@ -203,7 +203,7 @@ func (sb *Backend) NewWork() error {
 
 	sb.coreMu.RLock()
 	defer sb.coreMu.RUnlock()
-	if !sb.coreStarted {
+	if !sb.isCoreStarted() {
 		return istanbul.ErrStoppedEngine
 	}
 
```

### test/node.go
```diff
@@ -396,12 +396,9 @@ func NewNetwork(accounts *env.AccountsConfig, gc *genesis.Config, ec *eth.Config
 	// each other nodes don't start sending consensus messages to another node
 	// until they have received an enode certificate from that node.
 	for i, en := range enodes {
-		for j, n := range network {
-			if j == i {
-				continue
-			}
+		// Connect to the remaining nodes
+		for _, n := range network[i+1:] {
 			n.Server().AddPeer(en, p2p.ValidatorPurpose)
-			n.Server().AddTrustedPeer(en, p2p.ValidatorPurpose)
 		}
 	}
 
```
