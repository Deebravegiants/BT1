# [?] [SharovBot] Fix data race on bheapCache in db/rawdb (#19606)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-04
Source: https://github.com/erigontech/erigon/commit/9a00f9a7456004643c3d2bf98513fefc29a9d8fe
Type: security-commit

## Details
[SharovBot] Fix data race on bheapCache in db/rawdb (#19606)

**[SharovBot]**

## Summary
- Fix DATA RACE between `TestBlockStorage` and `TestBadBlocks` in
`db/rawdb`
- Add `sync.RWMutex` to protect concurrent access to the package-level
`bheapCache` variable
- The variable was being read in `TruncateCanonicalHash` and written in
`ResetBadBlockCache` without synchronization

## Test plan
- [x] `go test -race ./db/rawdb/... -run
"TestBlockStorage|TestBadBlocks" -count=3` passes with no DATA RACE
- [x] `go build ./...` passes
- [x] No test files modified

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### db/rawdb/accessors_chain.go
```diff
@@ -26,6 +26,7 @@ import (
 	"encoding/binary"
 	"fmt"
 	"math/big"
+	"sync"
 	"time"
 
 	"github.com/erigontech/erigon/common"
@@ -77,9 +78,11 @@ func TruncateCanonicalHash(tx kv.RwTx, blockFrom uint64, markChainAsBad bool) er
 				return err
 			}
 
+			bheapMu.Lock()
 			if bheapCache != nil {
 				heap.Push(bheapCache, &utils.BlockId{Number: binary.BigEndian.Uint64(blockNumBytes), Hash: common.BytesToHash(blockHash)})
 			}
+			bheapMu.Unlock()
 		}
 		return tx.Delete(kv.HeaderCanonical, blockNumBytes)
 	}); err != nil {
@@ -89,14 +92,24 @@ func TruncateCanonicalHash(tx kv.RwTx, blockFrom uint64, markChainAsBad bool) er
 }
 
 /* latest bad blocks start */
-var bheapCache utils.ExtendedHeap
+var (
+	bheapCache utils.ExtendedHeap
+	bheapMu    sync.RWMutex
+)
 
 func GetLatestBadBlocks(tx kv.Tx) ([]*types.Block, error) {
-	if bheapCache == nil {
+	bheapMu.RLock()
+	needsInit := bheapCache == nil
+	bheapMu.RUnlock()
+
+	if needsInit {
 		ResetBadBlockCache(tx, 100)
 	}
 
+	bheapMu.RLock()
 	blockIds := bheapCache.SortedValues()
+	bheapMu.RUnlock()
+
 	blocks := make([]*types.Block, len(blockIds))
 	for i, blockId := range blockIds {
 		blocks[i] = ReadBlock(tx, blockId.Hash, blockId.Number)
@@ -107,10 +120,14 @@ func GetLatestBadBlocks(tx kv.Tx) ([]*types.Block, error) {
 
 // mainly for testing purposes
 func ResetBadBlockCache(tx kv.Tx, limit int) error {
+	bheapMu.Lock()
 	bheapCache = utils.NewBlockMaxHeap(limit)
+	bheapMu.Unlock()
 	// load the heap
 	return tx.ForEach(kv.BadHeaderNumber, nil, func(blockHash, blockNumBytes []byte) error {
+		bheapMu.Lock()
 		heap.Push(bheapCache, &utils.BlockId{Number: binary.BigEndian.Uint64(blockNumBytes), Hash: common.BytesToHash(blockHash)})
+		bheapMu.Unlock()
 		return nil
 	})
 }
```
