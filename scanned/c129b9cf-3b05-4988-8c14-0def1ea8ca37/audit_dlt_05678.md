# [?] Fix panic in ethstats when block state is unavailable (#1778)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-12-18
Source: https://github.com/celo-org/celo-blockchain/commit/a0117f54daf8524a2be59e4e62a8b3f0442e2477
Type: security-commit

## Details
Fix panic in ethstats when block state is unavailable (#1778)

* check error from getting statedb for a block to avoid panic

* add a warning log statement

* 🤦

* Update ethstats/ethstats.go

Co-authored-by: piersy <pierspowlesland@gmail.com>

* remove unessasary change

Co-authored-by: piersy <pierspowlesland@gmail.com>
Co-authored-by: Gaston Ponti <pontigaston@gmail.com>

## Patch
### ethstats/ethstats.go
```diff
@@ -981,11 +981,10 @@ func (s *Service) assembleBlockStats(block *types.Block) *blockStats {
 	// Gather the block infos from the local blockchain
 	var (
 		header   *types.Header
-		stateDB  *state.StateDB
-		vmRunner vm.EVMRunner
 		td       *big.Int
 		txs      []txStats
 		valSet   validatorSet
+		gasLimit uint64
 	)
 
 	// check if backend is a full node
@@ -1009,8 +1008,6 @@ func (s *Service) assembleBlockStats(block *types.Block) *blockStats {
 		txs = []txStats{}
 	}
 	td = s.backend.GetTd(context.Background(), header.Hash())
-	stateDB, _, _ = s.backend.StateAndHeaderByNumberOrHash(context.Background(), rpc.BlockNumberOrHashWithHash(header.Hash(), true))
-	vmRunner = s.backend.NewEVMRunner(header, stateDB)
 
 	// Assemble and return the block stats
 	author, _ := s.engine.Author(header)
@@ -1019,12 +1016,20 @@ func (s *Service) assembleBlockStats(block *types.Block) *blockStats {
 	epochSize := s.engine.EpochSize()
 	blockRemain := epochSize - istanbul.GetNumberWithinEpoch(header.Number.Uint64(), epochSize)
 
-	// only assemble every valSetInterval blocks
-	if block != nil && block.Number().Uint64()%valSetInterval == 0 {
-		valSet = s.assembleValidatorSet(block, stateDB)
-	}
+	stateDB, _, err := s.backend.StateAndHeaderByNumberOrHash(context.Background(), rpc.BlockNumberOrHashWithHash(header.Hash(), true))
+
+	if err != nil {
+		log.Warn("Block state unavailable for reporting block stats", "hash", header.Hash(), "number", header.Number.Uint64(), "err", err)
+	} else {
 
-	gasLimit := blockchain_parameters.GetBlockGasLimitOrDefault(vmRunner)
+		// only assemble every valSetInterval blocks
+		if block != nil && block.Number().Uint64()%valSetInterval == 0 {
+			valSet = s.assembleValidatorSet(block, stateDB)
+		}
+
+		vmRunner := s.backend.NewEVMRunner(header, stateDB)
+		gasLimit = blockchain_parameters.GetBlockGasLimitOrDefault(vmRunner)
+	}
 
 	return &blockStats{
 		Number:      header.Number,
```
