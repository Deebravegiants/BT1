# [?] Fix data race: coreStarted (#1654)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-08-05
Source: https://github.com/celo-org/celo-blockchain/commit/1188111ac106a92c6c9d89c5ff3da265b404a161
Type: security-commit

## Details
Fix data race: coreStarted (#1654)

* Use coreMu to fix data race

## Patch
### consensus/istanbul/backend/api.go
```diff
@@ -190,22 +190,27 @@ func (api *API) GetVersionCertificateTableInfo() (map[string]*vet.VersionCertifi
 
 // GetCurrentRoundState retrieves the current IBFT RoundState
 func (api *API) GetCurrentRoundState() (*core.RoundStateSummary, error) {
+	api.istanbul.coreMu.RLock()
+	defer api.istanbul.coreMu.RUnlock()
+
 	if !api.istanbul.coreStarted {
 		return nil, istanbul.ErrStoppedEngine
 	}
 	return api.istanbul.core.CurrentRoundState().Summary(), nil
 }
 
-// GetCurrentRoundState retrieves the current IBFT RoundState
 func (api *API) ForceRoundChange() (bool, error) {
+	api.istanbul.coreMu.RLock()
+	defer api.istanbul.coreMu.RUnlock()
+
 	if !api.istanbul.coreStarted {
 		return false, istanbul.ErrStoppedEngine
 	}
 	api.istanbul.core.ForceRoundChange()
 	return true, nil
 }
 
-// Proxies retrieves all the proxied validator's proxies' info
+// GetProxiesInfo retrieves all the proxied validator's proxies' info
 func (api *API) GetProxiesInfo() ([]*proxy.ProxyInfo, error) {
 	if api.istanbul.IsProxiedValidator() {
 		proxies, valAssignments, err := api.istanbul.proxiedValidatorEngine.GetProxiesAndValAssignments()
```

### consensus/istanbul/backend/backend.go
```diff
@@ -231,7 +231,6 @@ type Backend struct {
 	validateState       func(block *types.Block, statedb *state.StateDB, receipts types.Receipts, usedGas uint64) error
 	onNewConsensusBlock func(block *types.Block, receipts []*types.Receipt, logs []*types.Log, state *state.StateDB)
 
-	// the channels for istanbul engine notifications
 	coreStarted bool
 	coreMu      sync.RWMutex
 
```

### consensus/istanbul/backend/engine.go
```diff
@@ -627,10 +627,12 @@ func (sb *Backend) updateReplicaStateLoop(bc *ethCore.BlockChain) {
 	for {
 		select {
 		case chainEvent := <-chainEventCh:
+			sb.coreMu.RLock()
 			if !sb.coreStarted && sb.replicaState != nil {
 				consensusBlock := new(big.Int).Add(chainEvent.Block.Number(), common.Big1)
 				sb.replicaState.NewChainHead(consensusBlock)
 			}
+			sb.coreMu.RUnlock()
 		case err := <-chainEventSub.Err():
 			log.Error("Error in istanbul's subscription to the blockchain's chain event", "err", err)
 			return
@@ -643,8 +645,8 @@ func (sb *Backend) SetCallBacks(hasBadBlock func(common.Hash) bool,
 	processBlock func(*types.Block, *state.StateDB) (types.Receipts, []*types.Log, uint64, error),
 	validateState func(*types.Block, *state.StateDB, types.Receipts, uint64) error,
 	onNewConsensusBlock func(block *types.Block, receipts []*types.Receipt, logs []*types.Log, state *state.StateDB)) error {
-	sb.coreMu.Lock()
-	defer sb.coreMu.Unlock()
+	sb.coreMu.RLock()
+	defer sb.coreMu.RUnlock()
 	if sb.coreStarted {
 		return istanbul.ErrStartedEngine
 	}
@@ -665,7 +667,7 @@ func (sb *Backend) StartValidating() error {
 	}
 
 	if sb.hasBadBlock == nil || sb.processBlock == nil || sb.validateState == nil {
-		return errors.New("Must SetBlockProcessors prior to StartValidating")
+		return errors.New("Must SetCallBacks prior to StartValidating")
 	}
 
 	sb.logger.Info("Starting istanbul.Engine validating")
```

### consensus/istanbul/backend/handler.go
```diff
@@ -197,7 +197,7 @@ func (sb *Backend) SetP2PServer(p2pserver consensus.P2PServer) {
 	sb.p2pserver = p2pserver
 }
 
-// This function is called by miner/worker.go whenever it's mainLoop gets a newWork event.
+// NewWork is called by miner/worker.go whenever it's mainLoop gets a newWork event.
 func (sb *Backend) NewWork() error {
 	sb.logger.Debug("NewWork called, acquiring core lock", "func", "NewWork")
 
```

### miner/worker.go
```diff
@@ -201,7 +201,6 @@ func (w *worker) start() {
 	}
 
 	if istanbul, ok := w.engine.(consensus.Istanbul); ok {
-
 		if istanbul.IsPrimary() {
 			istanbul.StartValidating()
 		}
```
