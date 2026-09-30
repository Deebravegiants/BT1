# [?] Fix data race issue for manager's lastState (#1046)

## Summary
Severity: Unknown
Chain: Rollkit
Component: rollkit/rollkit
Published: 2023-07-18
Source: https://github.com/evstack/ev-node/commit/f40c7c69a24b28d7d7e1d7ef1efbf1d76896a9e8
Type: security-commit

## Details
Fix data race issue for manager's lastState (#1046)

<!--
Please read and fill out this form before submitting your PR.

Please make sure you have reviewed our contributors guide before
submitting your
first PR.
-->

## Overview

Closes: #1047 

<!-- 
Please provide an explanation of the PR, including the appropriate
context,
background, goal, and rationale. If there is an issue with this
information,
please provide a tl;dr and link the issue. 
-->

## Checklist

<!-- 
Please complete the checklist to ensure that the PR is ready to be
reviewed.

IMPORTANT:
PRs should be left in Draft until the below checklist is completed.
-->

- [ ] New and updated code has appropriate documentation
- [ ] New and updated code has new and/or updated testing
- [ ] Required CI checks are passing
- [ ] Visual proof for any user facing features like CLI or
documentation updates
- [x] Linked issues closed with keywords

## Patch
### block/manager.go
```diff
@@ -13,6 +13,8 @@ import (
 	"github.com/libp2p/go-libp2p/core/crypto"
 	abci "github.com/tendermint/tendermint/abci/types"
 	tmcrypto "github.com/tendermint/tendermint/crypto"
+	tmstate "github.com/tendermint/tendermint/proto/tendermint/state"
+
 	"github.com/tendermint/tendermint/crypto/merkle"
 	"github.com/tendermint/tendermint/proxy"
 	tmtypes "github.com/tendermint/tendermint/types"
@@ -45,23 +47,23 @@ type newBlockEvent struct {
 // Manager is responsible for aggregating transactions into blocks.
 type Manager struct {
 	lastState types.State
+	// lastStateMtx is used by lastState
+	lastStateMtx *sync.RWMutex
+	store        store.Store
 
-	conf    config.BlockManagerConfig
-	genesis *tmtypes.GenesisDoc
-
+	conf        config.BlockManagerConfig
+	genesis     *tmtypes.GenesisDoc
 	proposerKey crypto.PrivKey
 
-	store    store.Store
 	executor *state.BlockExecutor
 
 	dalc      da.DataAvailabilityLayerClient
 	retriever da.BlockRetriever
 	// daHeight is the height of the latest processed DA block
 	daHeight uint64
 
-	HeaderCh chan *types.SignedHeader
-	BlockCh  chan *types.Block
-
+	HeaderCh  chan *types.SignedHeader
+	BlockCh   chan *types.Block
 	blockInCh chan newBlockEvent
 	syncCache map[uint64]*types.Block
 
@@ -70,8 +72,6 @@ type Manager struct {
 	// retrieveCond is used to notify sync goroutine (SyncLoop) that it needs to retrieve data
 	retrieveCond *sync.Cond
 
-	lastStateMtx *sync.Mutex
-
 	logger log.Logger
 
 	// For usage by Lazy Aggregator mode
@@ -155,7 +155,7 @@ func NewManager(
 		BlockCh:           make(chan *types.Block, 100),
 		blockInCh:         make(chan newBlockEvent, 100),
 		retrieveMtx:       new(sync.Mutex),
-		lastStateMtx:      new(sync.Mutex),
+		lastStateMtx:      new(sync.RWMutex),
 		syncCache:         make(map[uint64]*types.Block),
 		logger:            logger,
 		txsAvailable:      txsAvailableCh,
@@ -191,7 +191,8 @@ func (m *Manager) AggregationLoop(ctx context.Context, lazy bool) {
 	if height < initialHeight {
 		delay = time.Until(m.genesis.GenesisTime)
 	} else {
-		delay = time.Until(m.lastState.LastBlockTime.Add(m.conf.BlockTime))
+		lastBlockTime := m.getLastBlockTime()
+		delay = time.Until(lastBlockTime.Add(m.conf.BlockTime))
 	}
 
 	if delay > 0 {
@@ -339,7 +340,7 @@ func (m *Manager) trySyncNextBlock(ctx context.Context, daHeight uint64) error {
 
 	if b != nil && commit != nil {
 		m.logger.Info("Syncing block", "height", b.SignedHeader.Header.Height())
-		newState, responses, err := m.executor.ApplyBlock(ctx, m.lastState, b)
+		newState, responses, err := m.applyBlock(ctx, b)
 		if err != nil {
 			return fmt.Errorf("failed to ApplyBlock: %w", err)
 		}
@@ -358,7 +359,7 @@ func (m *Manager) trySyncNextBlock(ctx context.Context, daHeight uint64) error {
 		}
 
 		// SaveValidators commits the DB tx
-		err = m.store.SaveValidators(uint64(b.SignedHeader.Header.Height()), m.lastState.Validators)
+		err = m.saveValidatorsToStore(uint64(b.SignedHeader.Header.Height()))
 		if err != nil {
 			return err
 		}
@@ -368,10 +369,7 @@ func (m *Manager) trySyncNextBlock(ctx context.Context, daHeight uint64) error {
 		if daHeight > newState.DAHeight {
 			newState.DAHeight = daHeight
 		}
-		m.lastStateMtx.Lock()
-		m.lastState = newState
-		m.lastStateMtx.Unlock()
-		err = m.store.UpdateState(m.lastState)
+		err = m.updateState(newState)
 		if err != nil {
 			m.logger.Error("failed to save updated state", "error", err)
 		}
@@ -479,6 +477,8 @@ func (m *Manager) getCommit(header types.Header) (*types.Commit, error) {
 }
 
 func (m *Manager) IsProposer() (bool, error) {
+	m.lastStateMtx.RLock()
+	defer m.lastStateMtx.RUnlock()
 	// if proposer is not set, assume self proposer
 	if m.lastState.Validators.Proposer == nil {
 		return true, nil
@@ -499,9 +499,7 @@ func (m *Manager) publishBlock(ctx context.Context) error {
 	height := m.store.Height()
 	newHeight := height + 1
 
-	m.lastStateMtx.Lock()
 	isProposer, err := m.IsProposer()
-	m.lastStateMtx.Unlock()
 	if err != nil {
 		return fmt.Errorf("error while checking for proposer: %w", err)
 	}
@@ -535,7 +533,7 @@ func (m *Manager) publishBlock(ctx context.Context) error {
 		block = pendingBlock
 	} else {
 		m.logger.Info("Creating and publishing block", "height", newHeight)
-		block = m.executor.CreateBlock(newHeight, lastCommit, lastHeaderHash, m.lastState)
+		block = m.createBlock(newHeight, lastCommit, lastHeaderHash)
 		m.logger.Debug("block info", "num_tx", len(block.Data.Txs))
 
 		commit, err = m.getCommit(block.SignedHeader.Header)
@@ -546,7 +544,7 @@ func (m *Manager) publishBlock(ctx context.Context) error {
 		// set the commit to current block's signed header
 		block.SignedHeader.Commit = *commit
 
-		block.SignedHeader.Validators = m.lastState.Validators
+		block.SignedHeader.Validators = m.getLastStateValidators()
 
 		// SaveBlock commits the DB tx
 		err = m.store.SaveBlock(block, commit)
@@ -556,7 +554,7 @@ func (m *Manager) publishBlock(ctx context.Context) error {
 	}
 
 	// Apply the block but DONT commit
-	newState, responses, err := m.executor.ApplyBlock(ctx, m.lastState, block)
+	newState, responses, err := m.applyBlock(ctx, block)
 	if err != nil {
 		return err
 	}
@@ -595,7 +593,7 @@ func (m *Manager) publishBlock(ctx context.Context) error {
 	}
 
 	// SaveValidators commits the DB tx
-	err = m.store.SaveValidators(blockHeight, m.lastState.Validators)
+	err = m.saveValidatorsToStore(blockHeight)
 	if err != nil {
 		return err
 	}
@@ -605,10 +603,8 @@ func (m *Manager) publishBlock(ctx context.Context) error {
 
 	newState.DAHeight = atomic.LoadUint64(&m.daHeight)
 	// After this call m.lastState is the NEW state returned from ApplyBlock
-	m.lastState = newState
-
-	// UpdateState commits the DB tx
-	err = m.store.UpdateState(m.lastState)
+	// updateState also commits the DB tx
+	err = m.updateState(newState)
 	if err != nil {
 		return err
 	}
@@ -656,6 +652,47 @@ func (m *Manager) exponentialBackoff(backoff time.Duration) time.Duration {
 	return backoff
 }
 
+// Updates the state stored in manager's store along the manager's lastState
+func (m *Manager) updateState(s types.State) error {
+	m.lastStateMtx.Lock()
+	defer m.lastStateMtx.Unlock()
+	err := m.store.UpdateState(s)
+	if err != nil {
+		return err
+	}
+	m.lastState = s
+	return nil
+}
+
+func (m *Manager) saveValidatorsToStore(height uint64) error {
+	m.lastStateMtx.RLock()
+	defer m.lastStateMtx.RUnlock()
+	return m.store.SaveValidators(height, m.lastState.Validators)
+}
+
+func (m *Manager) getLastStateValidators() *tmtypes.ValidatorSet {
+	m.lastStateMtx.RLock()
+	defer m.lastStateMtx.RUnlock()
+	return m.lastState.Validators
+}
+
+func (m *Manager) getLastBlockTime() time.Time {
+	m.lastStateMtx.RLock()
+	defer m.lastStateMtx.RUnlock()
+	return m.lastState.LastBlockTime
+}
+
+func (m *Manager) createBlock(height uint64, lastCommit *types.Commit, lastHeaderHash types.Hash) *types.Block {
+	m.lastStateMtx.RLock()
+	defer m.lastStateMtx.RUnlock()
+	return m.executor.CreateBlock(height, lastCommit, lastHeaderHash, m.lastState)
+}
+
+func (m *Manager) applyBlock(ctx context.Context, block *types.Block) (types.State, *tmstate.ABCIResponses, error) {
+	m.lastStateMtx.RLock()
+	defer m.lastStateMtx.RUnlock()
+	return m.executor.ApplyBlock(ctx, m.lastState, block)
+}
 func updateState(s *types.State, res *abci.ResponseInitChain) {
 	// If the app did not return an app hash, we keep the one set from the genesis doc in
 	// the state. We don't set appHash since we don't want the genesis doc app hash
```

### block/manager_test.go
```diff
@@ -87,9 +87,11 @@ func TestInitialState(t *testing.T) {
 			agg, err := NewManager(key, conf, c.genesis, c.store, nil, nil, dalc, nil, logger, dumbChan)
 			assert.NoError(err)
 			assert.NotNil(agg)
+			agg.lastStateMtx.RLock()
 			assert.Equal(c.expectedChainID, agg.lastState.ChainID)
 			assert.Equal(c.expectedInitialHeight, agg.lastState.InitialHeight)
 			assert.Equal(c.expectedLastBlockHeight, agg.lastState.LastBlockHeight)
+			agg.lastStateMtx.RUnlock()
 		})
 	}
 }
```
