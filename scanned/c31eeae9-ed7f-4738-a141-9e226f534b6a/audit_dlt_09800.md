# [?] Fix for panic "insertChain failed to update current block" (#4612)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2024-01-18
Source: https://github.com/harmony-one/harmony/commit/e15bae129b23c68dcef58385ed787ba882292abf
Type: security-commit

## Details
Fix for panic "insertChain failed to update current block" (#4612)

## Patch
### core/blockchain_impl.go
```diff
@@ -31,6 +31,8 @@ import (
 	"sync/atomic"
 	"time"
 
+	"github.com/pkg/errors"
+
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/common/mclock"
 	"github.com/ethereum/go-ethereum/common/prque"
@@ -66,7 +68,6 @@ import (
 	"github.com/harmony-one/harmony/staking/slash"
 	staking "github.com/harmony-one/harmony/staking/types"
 	lru "github.com/hashicorp/golang-lru"
-	"github.com/pkg/errors"
 )
 
 var (
@@ -1730,21 +1731,16 @@ func (bc *BlockChainImpl) insertChain(chain types.Blocks, verifyHeaders bool) (i
 			err = NewBlockValidator(bc).ValidateBody(block)
 		}
 		switch {
-		case err == ErrKnownBlock:
-			// Block and state both already known. However if the current block is below
-			// this number we did a rollback and we should reimport it nonetheless.
-			if bc.CurrentBlock().NumberU64() >= block.NumberU64() {
-				stats.ignored++
-				continue
-			}
+		case errors.Is(err, ErrKnownBlock):
+			return i, events, coalescedLogs, err
 
 		case err == consensus_engine.ErrFutureBlock:
 			return i, events, coalescedLogs, err
 
-		case err == consensus_engine.ErrUnknownAncestor:
+		case errors.Is(err, consensus_engine.ErrUnknownAncestor):
 			return i, events, coalescedLogs, err
 
-		case err == consensus_engine.ErrPrunedAncestor:
+		case errors.Is(err, consensus_engine.ErrPrunedAncestor):
 			// TODO: add fork choice mechanism
 			// Block competing with the canonical chain, store in the db, but don't process
 			// until the competitor TD goes above the canonical TD
@@ -1771,9 +1767,7 @@ func (bc *BlockChainImpl) insertChain(chain types.Blocks, verifyHeaders bool) (i
 			// Prune in case non-empty winner chain
 			if len(winner) > 0 {
 				// Import all the pruned blocks to make the state available
-				bc.chainmu.Unlock()
 				_, evs, logs, err := bc.insertChain(winner, true /* verifyHeaders */)
-				bc.chainmu.Lock()
 				events, coalescedLogs = evs, logs
 
 				if err != nil {
@@ -1908,10 +1902,10 @@ func (bc *BlockChainImpl) insertChain(chain types.Blocks, verifyHeaders bool) (i
 
 // insertStats tracks and reports on block insertion.
 type insertStats struct {
-	queued, processed, ignored int
-	usedGas                    uint64
-	lastIndex                  int
-	startTime                  mclock.AbsTime
+	queued, processed int
+	usedGas           uint64
+	lastIndex         int
+	startTime         mclock.AbsTime
 }
 
 // statsReportLimit is the time limit during import and export after which we
@@ -1950,9 +1944,6 @@ func (st *insertStats) report(chain []*types.Block, index int, cache common.Stor
 		if st.queued > 0 {
 			context = context.Int("queued", st.queued)
 		}
-		if st.ignored > 0 {
-			context = context.Int("ignored", st.ignored)
-		}
 
 		logger := context.Logger()
 		logger.Info().Msg("Imported new chain segment")
```
