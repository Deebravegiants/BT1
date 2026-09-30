# [?] fix(chain): potential race condition to access best block

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2018-03-29
Source: https://github.com/vechain/thor/commit/01c3f17152bcb7dc754e24ec7dbe04d1f197ac55
Type: security-commit

## Details
fix(chain): potential race condition to access best block

## Patch
### chain/chain.go
```diff
@@ -3,6 +3,7 @@ package chain
 import (
 	"errors"
 	"sync"
+	"sync/atomic"
 
 	"github.com/vechain/thor/block"
 	"github.com/vechain/thor/chain/persist"
@@ -25,7 +26,7 @@ var errBlockExist = errors.New("block already exists")
 // It's thread-safe.
 type Chain struct {
 	kv        kv.GetPutter
-	bestBlock *block.Block
+	bestBlock atomic.Value
 	caches    caches
 	rw        sync.RWMutex
 }
@@ -113,7 +114,7 @@ func (c *Chain) WriteGenesis(genesis *block.Block) error {
 		if err := batch.Write(); err != nil {
 			return err
 		}
-		c.bestBlock = genesis
+		c.bestBlock.Store(genesis)
 		c.caches.block.Add(genesis.Header().ID(), newRawBlock(raw, genesis))
 		return nil
 	}
@@ -206,7 +207,7 @@ func (c *Chain) AddBlock(newBlock *block.Block, isTrunk bool) (*Fork, error) {
 	}
 
 	if isTrunk {
-		c.bestBlock = newBlock
+		c.bestBlock.Store(newBlock)
 	}
 	return fork, nil
 }
@@ -395,8 +396,8 @@ func (c *Chain) GetBestBlock() (*block.Block, error) {
 
 func (c *Chain) getBestBlock() (*block.Block, error) {
 
-	if best := c.bestBlock; best != nil {
-		return best, nil
+	if best := c.bestBlock.Load(); best != nil {
+		return best.(*block.Block), nil
 	}
 	id, err := persist.LoadBestBlockID(c.kv)
 	if err != nil {
@@ -406,7 +407,7 @@ func (c *Chain) getBestBlock() (*block.Block, error) {
 	if err != nil {
 		return nil, err
 	}
-	c.bestBlock = best
+	c.bestBlock.Store(best)
 	return best, nil
 }
 
```
