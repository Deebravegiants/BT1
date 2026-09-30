# [?] Fix data race on current (round state) access

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-09-22
Source: https://github.com/celo-org/celo-blockchain/commit/18bd409bf3c35f49780fb16efba7d01f0efa1882
Type: security-commit

## Details
Fix data race on current (round state) access

core.current was being read via calls to core.ParentCommits from the
worker's main loop, and written via calls to core.Stop coming from the
miner's update loop.

The fix is to add a mutext to synchronise access to current.

==================
WARNING: DATA RACE
Write at 0x00c00114dd98 by goroutine 329:
  github.com/celo-org/celo-blockchain/consensus/istanbul/core.(*core).Stop()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/core/handler.go:67 +0x8e
  github.com/celo-org/celo-blockchain/consensus/istanbul/backend.(*Backend).StopValidating()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/backend/engine.go:707 +0x193
  github.com/celo-org/celo-blockchain/miner.(*worker).stop()
      /home/pierspowlesland/projects/celo-blockchain/miner/worker.go:220 +0xbb
  github.com/celo-org/celo-blockchain/miner.(*Miner).update()
      /home/pierspowlesland/projects/celo-blockchain/miner/miner.go:173 +0x6fb

Previous read at 0x00c00114dd98 by goroutine 471:
  github.com/celo-org/celo-blockchain/consensus/istanbul/core.(*core).ParentCommits()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/core/core.go:204 +0x4a
  github.com/celo-org/celo-blockchain/consensus/istanbul/backend.(*Backend).addParentSeal.func1()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/backend/engine.go:989 +0x38a
  github.com/celo-org/celo-blockchain/consensus/istanbul/backend.(*Backend).addParentSeal()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/backend/engine.go:1019 +0x3ab
  github.com/celo-org/celo-blockchain/consensus/istanbul/backend.(*Backend).Prepare()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/backend/engine.go:404 +0x404
  github.com/celo-org/celo-blockchain/miner.prepareBlock()
      /home/pierspowlesland/projects/celo-blockchain/miner/block.go:89 +0x62f
  github.com/celo-org/celo-blockchain/miner.(*worker).constructAndSubmitNewBlock()
      /home/pierspowlesland/projects/celo-blockchain/miner/worker.go:242 +0x84
  github.com/celo-org/celo-blockchain/miner.(*worker).mainLoop.func1.1()
      /home/pierspowlesland/projects/celo-blockchain/miner/worker.go:379 +0x5c

## Patch
### consensus/istanbul/core/core.go
```diff
@@ -127,6 +127,7 @@ type core struct {
 
 	rsdb      RoundStateDB
 	current   RoundState
+	currentMu sync.RWMutex
 	handlerWg *sync.WaitGroup
 
 	roundChangeSet *roundChangeSet
@@ -200,6 +201,11 @@ func (c *core) CurrentView() *istanbul.View {
 func (c *core) CurrentRoundState() RoundState { return c.current }
 
 func (c *core) ParentCommits() MessageSet {
+	// ParentCommits is called by Prepare which is called by miner.worker the
+	// main loop, we need to synchronise this access with the write which
+	// occurs in Stop, which is called from the miner's update loop.
+	c.currentMu.RLock()
+	defer c.currentMu.RUnlock()
 	if c.current == nil {
 		return nil
 	}
```

### consensus/istanbul/core/handler.go
```diff
@@ -62,6 +62,8 @@ func (c *core) Stop() error {
 	// Make sure the handler goroutine exits
 	c.handlerWg.Wait()
 
+	c.currentMu.Lock()
+	defer c.currentMu.Unlock()
 	c.current = nil
 	return nil
 }
```
