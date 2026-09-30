# [?] fix: seal block if single tx overflows (#468)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2023-08-18
Source: https://github.com/scroll-tech/go-ethereum/commit/81dc3649a86d8da17025dbbd76c48addc4356fa9
Type: security-commit

## Details
fix: seal block if single tx overflows (#468)

## Patch
### miner/worker.go
```diff
@@ -273,6 +273,12 @@ func newWorker(config *Config, chainConfig *params.ChainConfig, engine consensus
 	return worker
 }
 
+// getCCC returns a pointer to this worker's CCC instance.
+// Only used in tests.
+func (w *worker) getCCC() *circuitcapacitychecker.CircuitCapacityChecker {
+	return w.circuitCapacityChecker
+}
+
 // setEtherbase sets the etherbase used to initialize the block coinbase field.
 func (w *worker) setEtherbase(addr common.Address) {
 	w.mu.Lock()
@@ -1065,13 +1071,23 @@ loop:
 			log.Trace("Circuit capacity limit reached for a single tx", "tx", tx.Hash().String(), "queueIndex", queueIndex)
 			log.Info("Skipping L1 message", "queueIndex", queueIndex, "tx", tx.Hash().String(), "block", w.current.header.Number, "reason", "row consumption overflow")
 			w.current.nextL1MsgIndex = queueIndex + 1
-			txs.Shift()
+
+			// after `ErrTxRowConsumptionOverflow`, ccc might not revert updates
+			// associated with this transaction so we cannot pack more transactions.
+			// TODO: fix this in ccc and change these lines back to `txs.Shift()`
+			circuitCapacityReached = true
+			break loop
 
 		case (errors.Is(err, circuitcapacitychecker.ErrTxRowConsumptionOverflow) && !tx.IsL1MessageTx()):
 			// Circuit capacity check: L2MessageTx row consumption too high, skip the account.
 			// This is also useful for skipping "problematic" L2MessageTxs.
 			log.Trace("Circuit capacity limit reached for a single tx", "tx", tx.Hash().String())
-			txs.Pop()
+
+			// after `ErrTxRowConsumptionOverflow`, ccc might not revert updates
+			// associated with this transaction so we cannot pack more transactions.
+			// TODO: fix this in ccc and change these lines back to `txs.Pop()`
+			circuitCapacityReached = true
+			break loop
 
 		case (errors.Is(err, circuitcapacitychecker.ErrUnknown) && tx.IsL1MessageTx()):
 			// Circuit capacity check: unknown circuit capacity checker error for L1MessageTx,
@@ -1080,12 +1096,22 @@ loop:
 			log.Trace("Unknown circuit capacity checker error for L1MessageTx", "tx", tx.Hash().String(), "queueIndex", queueIndex)
 			log.Info("Skipping L1 message", "queueIndex", queueIndex, "tx", tx.Hash().String(), "block", w.current.header.Number, "reason", "unknown row consumption error")
 			w.current.nextL1MsgIndex = queueIndex + 1
-			txs.Shift()
+
+			// after `ErrUnknown`, ccc might not revert updates associated
+			// with this transaction so we cannot pack more transactions.
+			// TODO: fix this in ccc and change these lines back to `txs.Shift()`
+			circuitCapacityReached = true
+			break loop
 
 		case (errors.Is(err, circuitcapacitychecker.ErrUnknown) && !tx.IsL1MessageTx()):
 			// Circuit capacity check: unknown circuit capacity checker error for L2MessageTx, skip the account
 			log.Trace("Unknown circuit capacity checker error for L2MessageTx", "tx", tx.Hash().String())
-			txs.Pop()
+
+			// after `ErrUnknown`, ccc might not revert updates associated
+			// with this transaction so we cannot pack more transactions.
+			// TODO: fix this in ccc and change these lines back to `txs.Pop()`
+			circuitCapacityReached = true
+			break loop
 
 		default:
 			// Strange error, discard the transaction and get the next in line (note, the
```

### miner/worker_test.go
```diff
@@ -38,6 +38,7 @@ import (
 	"github.com/scroll-tech/go-ethereum/ethdb"
 	"github.com/scroll-tech/go-ethereum/event"
 	"github.com/scroll-tech/go-ethereum/params"
+	"github.com/scroll-tech/go-ethereum/rollup/circuitcapacitychecker"
 	"github.com/scroll-tech/go-ethereum/rollup/sync_service"
 )
 
@@ -732,7 +733,7 @@ func TestL1MsgCorrectOrder(t *testing.T) {
 	}
 }
 
-func l1MessageTest(t *testing.T, msgs []types.L1MessageTx, withL2Tx bool, callback func(i int, block *types.Block, db ethdb.Database) bool) {
+func l1MessageTest(t *testing.T, msgs []types.L1MessageTx, withL2Tx bool, callback func(i int, block *types.Block, db ethdb.Database, w *worker) bool) {
 	var (
 		engine      consensus.Engine
 		chainConfig *params.ChainConfig
@@ -777,6 +778,9 @@ func l1MessageTest(t *testing.T, msgs []types.L1MessageTx, withL2Tx bool, callba
 	// Start mining!
 	w.start()
 
+	// call once before first block
+	callback(0, nil, db, w)
+
 	// timeout for all blocks
 	globalTimeout := time.After(3 * time.Second)
 
@@ -790,8 +794,8 @@ func l1MessageTest(t *testing.T, msgs []types.L1MessageTx, withL2Tx bool, callba
 		select {
 		case ev := <-sub.Chan():
 			block := ev.Data.(core.NewMinedBlockEvent).Block
-			// TODO
-			if callback(ii, block, db) {
+
+			if done := callback(ii, block, db, w); done {
 				return
 			}
 
@@ -811,21 +815,28 @@ func TestL1SingleMessageOverGasLimit(t *testing.T) {
 		{QueueIndex: 2, Gas: 21016, To: &common.Address{1}, Data: []byte{0x01}, Sender: common.Address{3}},    // different sender
 	}
 
-	l1MessageTest(t, msgs, false, func(_i int, block *types.Block, db ethdb.Database) bool {
-		// skip #0, include #1 and #2
-		assert.Equal(2, len(block.Transactions()))
+	l1MessageTest(t, msgs, false, func(blockNum int, block *types.Block, db ethdb.Database, w *worker) bool {
+		switch blockNum {
+		case 0:
+			return false
+		case 1:
+			// skip #0, include #1 and #2
+			assert.Equal(2, len(block.Transactions()))
 
-		assert.True(block.Transactions()[0].IsL1MessageTx())
-		assert.Equal(uint64(1), block.Transactions()[0].AsL1MessageTx().QueueIndex)
-		assert.True(block.Transactions()[1].IsL1MessageTx())
-		assert.Equal(uint64(2), block.Transactions()[1].AsL1MessageTx().QueueIndex)
+			assert.True(block.Transactions()[0].IsL1MessageTx())
+			assert.Equal(uint64(1), block.Transactions()[0].AsL1MessageTx().QueueIndex)
+			assert.True(block.Transactions()[1].IsL1MessageTx())
+			assert.Equal(uint64(2), block.Transactions()[1].AsL1MessageTx().QueueIndex)
 
-		// db is updated correctly
-		queueIndex := rawdb.ReadFirstQueueIndexNotInL2Block(db, block.Hash())
-		assert.NotNil(queueIndex)
-		assert.Equal(uint64(3), *queueIndex)
+			// db is updated correctly
+			queueIndex := rawdb.ReadFirstQueueIndexNotInL2Block(db, block.Hash())
+			assert.NotNil(queueIndex)
+			assert.Equal(uint64(3), *queueIndex)
 
-		return true
+			return true
+		default:
+			return true
+		}
 	})
 }
 
@@ -840,8 +851,10 @@ func TestL1CombinedMessagesOverGasLimit(t *testing.T) {
 		{QueueIndex: 2, Gas: 21016, To: &common.Address{1}, Data: []byte{0x01}, Sender: common.Address{3}},   // different sender
 	}
 
-	l1MessageTest(t, msgs, false, func(blockNum int, block *types.Block, db ethdb.Database) bool {
+	l1MessageTest(t, msgs, false, func(blockNum int, block *types.Block, db ethdb.Database, w *worker) bool {
 		switch blockNum {
+		case 0:
+			return false
 		case 1:
 			// block #1 only includes 1 message
 			assert.Equal(1, len(block.Transactions()))
@@ -882,23 +895,30 @@ func TestLargeL1MessageSkipPayloadCheck(t *testing.T) {
 		{QueueIndex: 2, Gas: 21016, To: &common.Address{1}, Data: []byte{0x01}, Sender: common.Address{3}}, // different sender
 	}
 
-	l1MessageTest(t, msgs, false, func(blockNum int, block *types.Block, db ethdb.Database) bool {
-		// include #0, #1 and #2
-		assert.Equal(3, len(block.Transactions()))
+	l1MessageTest(t, msgs, false, func(blockNum int, block *types.Block, db ethdb.Database, w *worker) bool {
+		switch blockNum {
+		case 0:
+			return false
+		case 1:
+			// include #0, #1 and #2
+			assert.Equal(3, len(block.Transactions()))
 
-		assert.True(block.Transactions()[0].IsL1MessageTx())
-		assert.Equal(uint64(0), block.Transactions()[0].AsL1MessageTx().QueueIndex)
-		assert.True(block.Transactions()[1].IsL1MessageTx())
-		assert.Equal(uint64(1), block.Transactions()[1].AsL1MessageTx().QueueIndex)
-		assert.True(block.Transactions()[2].IsL1MessageTx())
-		assert.Equal(uint64(2), block.Transactions()[2].AsL1MessageTx().QueueIndex)
+			assert.True(block.Transactions()[0].IsL1MessageTx())
+			assert.Equal(uint64(0), block.Transactions()[0].AsL1MessageTx().QueueIndex)
+			assert.True(block.Transactions()[1].IsL1MessageTx())
+			assert.Equal(uint64(1), block.Transactions()[1].AsL1MessageTx().QueueIndex)
+			assert.True(block.Transactions()[2].IsL1MessageTx())
+			assert.Equal(uint64(2), block.Transactions()[2].AsL1MessageTx().QueueIndex)
 
-		// db is updated correctly
-		queueIndex := rawdb.ReadFirstQueueIndexNotInL2Block(db, block.Hash())
-		assert.NotNil(queueIndex)
-		assert.Equal(uint64(3), *queueIndex)
+			// db is updated correctly
+			queueIndex := rawdb.ReadFirstQueueIndexNotInL2Block(db, block.Hash())
+			assert.NotNil(queueIndex)
+			assert.Equal(uint64(3), *queueIndex)
 
-		return true
+			return true
+		default:
+			return true
+		}
 	})
 }
 
@@ -913,22 +933,29 @@ func TestSkipMessageWithStrangeError(t *testing.T) {
 		{QueueIndex: 2, Gas: 21016, To: &common.Address{1}, Data: []byte{0x01}, Sender: common.Address{3}},
 	}
 
-	l1MessageTest(t, msgs, false, func(blockNum int, block *types.Block, db ethdb.Database) bool {
-		// skip #0, include #1 and #2
-		assert.Equal(2, len(block.Transactions()))
-		assert.True(block.Transactions()[0].IsL1MessageTx())
+	l1MessageTest(t, msgs, false, func(blockNum int, block *types.Block, db ethdb.Database, w *worker) bool {
+		switch blockNum {
+		case 0:
+			return false
+		case 1:
+			// skip #0, include #1 and #2
+			assert.Equal(2, len(block.Transactions()))
+			assert.True(block.Transactions()[0].IsL1MessageTx())
 
-		assert.True(block.Transactions()[0].IsL1MessageTx())
-		assert.Equal(uint64(1), block.Transactions()[0].AsL1MessageTx().QueueIndex)
-		assert.True(block.Transactions()[1].IsL1MessageTx())
-		assert.Equal(uint64(2), block.Transactions()[1].AsL1MessageTx().QueueIndex)
+			assert.True(block.Transactions()[0].IsL1MessageTx())
+			assert.Equal(uint64(1), block.Transactions()[0].AsL1MessageTx().QueueIndex)
+			assert.True(block.Transactions()[1].IsL1MessageTx())
+			assert.Equal(uint64(2), block.Transactions()[1].AsL1MessageTx().QueueIndex)
 
-		// db is updated correctly
-		queueIndex := rawdb.ReadFirstQueueIndexNotInL2Block(db, block.Hash())
-		assert.NotNil(queueIndex)
-		assert.Equal(uint64(3), *queueIndex)
+			// db is updated correctly
+			queueIndex := rawdb.ReadFirstQueueIndexNotInL2Block(db, block.Hash())
+			assert.NotNil(queueIndex)
+			assert.Equal(uint64(3), *queueIndex)
 
-		return true
+			return true
+		default:
+			return false
+		}
 	})
 }
 
@@ -943,18 +970,59 @@ func TestSkipAllL1MessagesInBlock(t *testing.T) {
 		{QueueIndex: 2, Gas: 21016, To: &common.Address{1}, Data: []byte{0x01}, Sender: common.Address{3}, Value: big.NewInt(1)},
 	}
 
-	l1MessageTest(t, msgs, true, func(blockNum int, block *types.Block, db ethdb.Database) bool {
-		// skip all 3 L1 messages, include 1 L2 tx
-		assert.Equal(1, len(block.Transactions()))
-		assert.False(block.Transactions()[0].IsL1MessageTx())
+	l1MessageTest(t, msgs, true, func(blockNum int, block *types.Block, db ethdb.Database, w *worker) bool {
+		switch blockNum {
+		case 0:
+			return false
+		case 1:
+			// skip all 3 L1 messages, include 1 L2 tx
+			assert.Equal(1, len(block.Transactions()))
+			assert.False(block.Transactions()[0].IsL1MessageTx())
 
-		// db is updated correctly
-		// note: this should return 0 but on the signer we store 3 instead so
-		// that we do not process the same messages again for the next block.
-		queueIndex := rawdb.ReadFirstQueueIndexNotInL2Block(db, block.Hash())
-		assert.NotNil(queueIndex)
-		assert.Equal(uint64(3), *queueIndex)
+			// db is updated correctly
+			// note: this should return 0 but on the signer we store 3 instead so
+			// that we do not process the same messages again for the next block.
+			queueIndex := rawdb.ReadFirstQueueIndexNotInL2Block(db, block.Hash())
+			assert.NotNil(queueIndex)
+			assert.Equal(uint64(3), *queueIndex)
 
-		return true
+			return true
+		default:
+			return true
+		}
+	})
+}
+
+func TestOversizedTxThenNormal(t *testing.T) {
+	assert := assert.New(t)
+
+	msgs := []types.L1MessageTx{
+		{QueueIndex: 0, Gas: 25100, To: &common.Address{1}, Data: []byte{0x01}, Sender: common.Address{2}},
+		{QueueIndex: 1, Gas: 21016, To: &common.Address{1}, Data: []byte{0x01}, Sender: common.Address{2}},
+		{QueueIndex: 2, Gas: 21016, To: &common.Address{1}, Data: []byte{0x01}, Sender: common.Address{3}},
+	}
+
+	l1MessageTest(t, msgs, false, func(blockNum int, block *types.Block, db ethdb.Database, w *worker) bool {
+		switch blockNum {
+		case 0:
+			// schedule to skip 2nd call to ccc
+			w.getCCC().ScheduleError(2, circuitcapacitychecker.ErrTxRowConsumptionOverflow)
+			return false
+		case 1:
+			// include #0, skip #1, then terminate
+			assert.Equal(1, len(block.Transactions()))
+
+			assert.True(block.Transactions()[0].IsL1MessageTx())
+			assert.Equal(uint64(0), block.Transactions()[0].AsL1MessageTx().QueueIndex)
+
+			// db is updated correctly
+			queueIndex := rawdb.ReadFirstQueueIndexNotInL2Block(db, block.Hash())
+			assert.NotNil(queueIndex)
+			assert.Equal(uint64(2), *queueIndex)
+
+			return true
+		default:
+			return true
+		}
 	})
 }
```

### params/version.go
```diff
@@ -24,7 +24,7 @@ import (
 const (
 	VersionMajor = 4         // Major version component of the current release
 	VersionMinor = 3         // Minor version component of the current release
-	VersionPatch = 38        // Patch version component of the current release
+	VersionPatch = 39        // Patch version component of the current release
 	VersionMeta  = "sepolia" // Version metadata to append to the version string
 )
 
```

### rollup/circuitcapacitychecker/mock.go
```diff
@@ -9,7 +9,9 @@ import (
 )
 
 type CircuitCapacityChecker struct {
-	ID uint64
+	ID        uint64
+	countdown int
+	nextError *error
 }
 
 func NewCircuitCapacityChecker() *CircuitCapacityChecker {
@@ -20,6 +22,14 @@ func (ccc *CircuitCapacityChecker) Reset() {
 }
 
 func (ccc *CircuitCapacityChecker) ApplyTransaction(traces *types.BlockTrace) (*types.RowConsumption, error) {
+	if ccc.nextError != nil {
+		ccc.countdown--
+		if ccc.countdown == 0 {
+			err := *ccc.nextError
+			ccc.nextError = nil
+			return nil, err
+		}
+	}
 	return &types.RowConsumption{types.SubCircuitRowUsage{
 		Name:      "mock",
 		RowNumber: 1,
@@ -32,3 +42,8 @@ func (ccc *CircuitCapacityChecker) ApplyBlock(traces *types.BlockTrace) (*types.
 		RowNumber: 2,
 	}}, nil
 }
+
+func (ccc *CircuitCapacityChecker) ScheduleError(cnt int, err error) {
+	ccc.countdown = cnt
+	ccc.nextError = &err
+}
```
