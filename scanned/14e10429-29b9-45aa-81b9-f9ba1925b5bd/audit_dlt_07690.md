# [?] privateapi: fix ethbackend.Syncing api nil dereference (#12711)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2024-11-12
Source: https://github.com/erigontech/erigon/commit/be202f7359b5103ce543c2587d6b17d8b8006fdb
Type: security-commit

## Details
privateapi: fix ethbackend.Syncing api nil dereference (#12711)

## Patch
### core/rawdb/accessors_chain.go
```diff
@@ -1337,14 +1337,3 @@ func ReadDBSchemaVersion(tx kv.Tx) (major, minor, patch uint32, ok bool, err err
 	patch = binary.BigEndian.Uint32(existingVersion[8:])
 	return major, minor, patch, true, nil
 }
-
-func ReadLastNewBlockSeen(tx kv.Tx) (uint64, error) {
-	v, err := tx.GetOne(kv.SyncStageProgress, kv.LastNewBlockSeen)
-	if err != nil {
-		return 0, err
-	}
-	if len(v) == 0 {
-		return 0, nil
-	}
-	return dbutils.DecodeBlockNumber(v)
-}
```

### erigon-lib/kv/tables.go
```diff
@@ -484,7 +484,6 @@ var (
 	PlainStateVersion = []byte("PlainStateVersion")
 
 	HighestFinalizedKey = []byte("HighestFinalized")
-	LastNewBlockSeen    = []byte("LastNewBlockSeen") // last seen block hash
 
 	StatesProcessingKey          = []byte("StatesProcessing")
 	MinimumPrunableStepDomainKey = []byte("MinimumPrunableStepDomainKey")
```

### ethdb/privateapi/ethbackend.go
```diff
@@ -22,7 +22,6 @@ import (
 	"errors"
 	"math"
 
-	"github.com/erigontech/erigon/eth/stagedsync/stages"
 	"google.golang.org/protobuf/types/known/emptypb"
 
 	libcommon "github.com/erigontech/erigon-lib/common"
@@ -32,8 +31,8 @@ import (
 	types2 "github.com/erigontech/erigon-lib/gointerfaces/typesproto"
 	"github.com/erigontech/erigon-lib/kv"
 	"github.com/erigontech/erigon-lib/log/v3"
-
 	"github.com/erigontech/erigon/common"
+	"github.com/erigontech/erigon/eth/stagedsync/stages"
 	"github.com/erigontech/erigon/params"
 	"github.com/erigontech/erigon/rlp"
 	"github.com/erigontech/erigon/turbo/builder"
@@ -141,29 +140,29 @@ func (s *EthBackendServer) Syncing(ctx context.Context, _ *emptypb.Empty) (*remo
 	reply := &remote.SyncingReply{
 		CurrentBlock:     currentBlock,
 		FrozenBlocks:     frozenBlocks,
-		LastNewBlockSeen: math.MaxUint64,
+		LastNewBlockSeen: highestBlock,
+		Syncing:          true,
 	}
 
 	// Maybe it is still downloading snapshots. Impossible to determine the highest block.
 	if highestBlock == 0 {
-		reply.Syncing = true
 		return reply, nil
 	}
-	reorgRange := 8
 
 	// If the distance between the current block and the highest block is less than the reorg range, we are not syncing. abs(highestBlock - currentBlock) < reorgRange
+	reorgRange := 8
 	if math.Abs(float64(highestBlock)-float64(currentBlock)) < float64(reorgRange) {
 		reply.Syncing = false
 		return reply, nil
 	}
 
-	reply.LastNewBlockSeen = highestBlock
 	reply.Stages = make([]*remote.SyncingReply_StageProgress, len(stages.AllStages))
 	for i, stage := range stages.AllStages {
 		progress, err := stages.GetStageProgress(tx, stage)
 		if err != nil {
 			return nil, err
 		}
+		reply.Stages[i] = &remote.SyncingReply_StageProgress{}
 		reply.Stages[i].StageName = string(stage)
 		reply.Stages[i].BlockNumber = progress
 	}
```

### turbo/jsonrpc/eth_system.go
```diff
@@ -18,21 +18,17 @@ package jsonrpc
 
 import (
 	"context"
-	"math"
 	"math/big"
 
+	"github.com/erigontech/erigon-lib/chain"
 	"github.com/erigontech/erigon-lib/common"
 	"github.com/erigontech/erigon-lib/common/hexutil"
-
-	"github.com/erigontech/erigon-lib/chain"
 	"github.com/erigontech/erigon-lib/kv"
-
 	"github.com/erigontech/erigon/consensus/misc"
 	"github.com/erigontech/erigon/core/rawdb"
 	"github.com/erigontech/erigon/core/types"
 	"github.com/erigontech/erigon/eth/ethconfig"
 	"github.com/erigontech/erigon/eth/gasprice"
-	"github.com/erigontech/erigon/eth/stagedsync/stages"
 	"github.com/erigontech/erigon/rpc"
 	"github.com/erigontech/erigon/turbo/rpchelper"
 )
@@ -57,37 +53,25 @@ func (api *APIImpl) Syncing(ctx context.Context) (interface{}, error) {
 	if err != nil {
 		return false, err
 	}
-	highestBlock := reply.LastNewBlockSeen
-	currentBlock := reply.CurrentBlock
-
-	// Maybe it is still downloading snapshots. Impossible to determine the highest block.
-	if highestBlock == 0 {
-		return map[string]interface{}{
-			"startingBlock": "0x0", // TODO: this is a placeholder, I do not think it matters what we return here, but 0x0 is probably a good placeholder.
-			"currentBlock":  hexutil.Uint64(currentBlock),
-			"highestBlock":  hexutil.Uint64(math.MaxUint64),
-		}, nil
-	}
-	reorgRange := 8
-
-	// If the distance between the current block and the highest block is less than the reorg range, we are not syncing. abs(highestBlock - currentBlock) < reorgRange
-	if math.Abs(float64(highestBlock)-float64(currentBlock)) < float64(reorgRange) {
+	if !reply.Syncing {
 		return false, nil
 	}
 
-	// Otherwise gather the block sync stats
+	// Still sync-ing, gather the block sync stats
+	highestBlock := reply.LastNewBlockSeen
+	currentBlock := reply.CurrentBlock
 	type S struct {
 		StageName   string         `json:"stage_name"`
 		BlockNumber hexutil.Uint64 `json:"block_number"`
 	}
-	stagesMap := make([]S, len(stages.AllStages))
+	stagesMap := make([]S, len(reply.Stages))
 	for i, stage := range reply.Stages {
 		stagesMap[i].StageName = stage.StageName
 		stagesMap[i].BlockNumber = hexutil.Uint64(stage.BlockNumber)
 	}
 
 	return map[string]interface{}{
-		"startingBlock": "0x0", // TODO: this is a placeholder, I do not think it matters what we return here, but 0x0 is probably a good placeholder.
+		"startingBlock": "0x0", // 0x0 is a placeholder, I do not think it matters what we return here
 		"currentBlock":  hexutil.Uint64(currentBlock),
 		"highestBlock":  hexutil.Uint64(highestBlock),
 		"stages":        stagesMap,
```
