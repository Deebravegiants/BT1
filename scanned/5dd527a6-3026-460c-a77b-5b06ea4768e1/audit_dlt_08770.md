# [?] miner: fix data race on setting etherbase/extradata

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2016-12-13
Source: https://github.com/scroll-tech/go-ethereum/commit/dadd68935935388b158a510c95b8644be44073ce
Type: security-commit

## Details
miner: fix data race on setting etherbase/extradata

## Patch
### miner/miner.go
```diff
@@ -119,25 +119,22 @@ func (m *Miner) SetGasPrice(price *big.Int) {
 
 func (self *Miner) Start(coinbase common.Address, threads int) {
 	atomic.StoreInt32(&self.shouldStart, 1)
-	self.threads = threads
-	self.worker.coinbase = coinbase
+	self.worker.setEtherbase(coinbase)
 	self.coinbase = coinbase
+	self.threads = threads
 
 	if atomic.LoadInt32(&self.canStart) == 0 {
 		glog.V(logger.Info).Infoln("Can not start mining operation due to network sync (starts when finished)")
 		return
 	}
-
 	atomic.StoreInt32(&self.mining, 1)
 
 	for i := 0; i < threads; i++ {
 		self.worker.register(NewCpuAgent(i, self.pow))
 	}
 
 	glog.V(logger.Info).Infof("Starting mining operation (CPU=%d TOT=%d)\n", threads, len(self.worker.agents))
-
 	self.worker.start()
-
 	self.worker.commitNewWork()
 }
 
@@ -177,8 +174,7 @@ func (self *Miner) SetExtra(extra []byte) error {
 	if uint64(len(extra)) > params.MaximumExtraDataSize.Uint64() {
 		return fmt.Errorf("Extra exceeds max length. %d > %v", len(extra), params.MaximumExtraDataSize)
 	}
-
-	self.worker.extra = extra
+	self.worker.setExtra(extra)
 	return nil
 }
 
@@ -188,9 +184,9 @@ func (self *Miner) Pending() (*types.Block, *state.StateDB) {
 }
 
 // PendingBlock returns the currently pending block.
-// 
-// Note, to access both the pending block and the pending state 
-// simultaneously, please use Pending(), as the pending state can 
+//
+// Note, to access both the pending block and the pending state
+// simultaneously, please use Pending(), as the pending state can
 // change between multiple method calls
 func (self *Miner) PendingBlock() *types.Block {
 	return self.worker.pendingBlock()
```

### miner/worker.go
```diff
@@ -161,6 +161,12 @@ func (self *worker) setEtherbase(addr common.Address) {
 	self.coinbase = addr
 }
 
+func (self *worker) setExtra(extra []byte) {
+	self.mu.Lock()
+	defer self.mu.Unlock()
+	self.extra = extra
+}
+
 func (self *worker) pending() (*types.Block, *state.StateDB) {
 	self.currentMu.Lock()
 	defer self.currentMu.Unlock()
```
