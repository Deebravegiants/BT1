# [?] kaiax/gov: fix nil-header panic when rebuilding gov/vote cache

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2026-06-18
Source: https://github.com/kaiachain/kaia/commit/66f6fd1eddbdba1073626e012e162d4733d95d41
Type: security-commit

## Details
kaiax/gov: fix nil-header panic when rebuilding gov/vote cache

readGovDataFromDB/readVoteDataFromDB dereferenced headers fetched from the
persisted gov/vote block-number index without a nil check, panicking on every
startup when the index and header DB diverged — for example when the index
lists a block above the current head that is no longer canonical. Since the
same index is read on each restart, this could become a restart loop.

Skip a block whose header is above the current head; a missing header at or
below the head means the canonical chain is broken and is fatal. The shared
loop is extracted into forEachIndexedHeader. The in-memory cache is recomputed
on every startup, so the stale index is left untouched.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

## Patch
### kaiax/gov/headergov/impl/init.go
```diff
@@ -7,6 +7,7 @@ import (
 	"sync/atomic"
 	"time"
 
+	"github.com/kaiachain/kaia/blockchain/types"
 	"github.com/kaiachain/kaia/common"
 	"github.com/kaiachain/kaia/consensus"
 	"github.com/kaiachain/kaia/kaiax/gov"
@@ -280,43 +281,55 @@ func (h *headerGovModule) accumulateVotesInEpoch(epochIdx uint64) {
 	logger.Info("Accumulated votes", "epochIdx", epochIdx)
 }
 
-func readVoteDataFromDB(chain chain, db database.Database) map[uint64]headergov.VoteData {
-	voteBlocks := ReadVoteDataBlockNums(db)
-	votes := make(map[uint64]headergov.VoteData)
-	for _, blockNum := range voteBlocks {
+// forEachIndexedHeader calls fn for each indexed block whose header is present. A block
+// above head is no longer on the canonical chain, so it is skipped; a missing header at or
+// below head means the canonical chain is broken (fatal).
+func forEachIndexedHeader(chain chain, blockNums StoredUint64Array, kind string, fn func(blockNum uint64, header *types.Header)) {
+	head := chain.CurrentBlock().NumberU64()
+	for _, blockNum := range blockNums {
 		header := chain.GetHeaderByNumber(blockNum)
-		parsedVote, err := headergov.VoteBytes(header.Vote).ToVoteData()
-		if err != nil {
-			panic(err)
+		if header == nil {
+			if blockNum > head {
+				logger.Warn("Skipping stale block above head", "kind", kind, "num", blockNum, "head", head)
+				continue
+			}
+			logger.Crit("Missing canonical header for indexed block", "kind", kind, "num", blockNum, "head", head)
 		}
 
-		votes[blockNum] = parsedVote
+		fn(blockNum, header)
 	}
+}
 
+func readVoteDataFromDB(chain chain, db database.Database) map[uint64]headergov.VoteData {
+	votes := make(map[uint64]headergov.VoteData)
+	forEachIndexedHeader(chain, ReadVoteDataBlockNums(db), "vote",
+		func(blockNum uint64, header *types.Header) {
+			parsedVote, err := headergov.VoteBytes(header.Vote).ToVoteData()
+			if err != nil {
+				panic(err)
+			}
+			votes[blockNum] = parsedVote
+		},
+	)
 	return votes
 }
 
 func readGovDataFromDB(chain chain, db database.Database) map[uint64]headergov.GovData {
-	govBlocks := ReadGovDataBlockNums(db)
 	govs := make(map[uint64]headergov.GovData)
-
-	for _, blockNum := range govBlocks {
-		header := chain.GetHeaderByNumber(blockNum)
-
-		parsedGov, err := headergov.GovBytes(header.Governance).ToGovData()
-		if err != nil {
-			// For tests, genesis' governance can be nil.
-			if blockNum == 0 {
-				continue
+	forEachIndexedHeader(chain, ReadGovDataBlockNums(db), "gov",
+		func(blockNum uint64, header *types.Header) {
+			parsedGov, err := headergov.GovBytes(header.Governance).ToGovData()
+			if err != nil {
+				// For tests, genesis' governance can be nil: omit from cache.
+				if blockNum == 0 {
+					return
+				}
+				logger.Error("Failed to parse gov", "num", blockNum, "err", err)
+				panic("failed to parse gov")
 			}
-
-			logger.Error("Failed to parse gov", "num", blockNum, "err", err)
-			panic("failed to parse gov")
-		}
-
-		govs[blockNum] = parsedGov
-	}
-
+			govs[blockNum] = parsedGov
+		},
+	)
 	return govs
 }
 
```

### kaiax/gov/headergov/impl/init_test.go
```diff
@@ -102,6 +102,7 @@ func TestReadGovVoteBlockNumsFromDB(t *testing.T) {
 
 	mockCtrl := gomock.NewController(t)
 	chain := mocks.NewMockBlockChain(mockCtrl)
+	chain.EXPECT().CurrentBlock().Return(types.NewBlockWithHeader(&types.Header{Number: big.NewInt(100)})).AnyTimes()
 
 	db := database.NewMemDB()
 	voteDataBlockNums := make(StoredUint64Array, 0, len(votes))
@@ -119,6 +120,7 @@ func TestReadGovVoteBlockNumsFromDB(t *testing.T) {
 func TestReadGovDataFromDB(t *testing.T) {
 	mockCtrl := gomock.NewController(t)
 	chain := mocks.NewMockBlockChain(mockCtrl)
+	chain.EXPECT().CurrentBlock().Return(types.NewBlockWithHeader(&types.Header{Number: big.NewInt(2)})).AnyTimes()
 	db := database.NewMemDB()
 
 	ps1 := &gov.ParamSet{UnitPrice: uint64(100)}
@@ -139,6 +141,41 @@ func TestReadGovDataFromDB(t *testing.T) {
 	assert.Equal(t, govs, readGovDataFromDB(chain, db))
 }
 
+// mockChainWithStaleBlock sets up head=2 with a gov/vote index {1, 9}, where block 1 has
+// header1 and block 9's header is missing (nil) — i.e. a stale block above head.
+func mockChainWithStaleBlock(t *testing.T, header1 *types.Header, writeIndex func(database.Database, StoredUint64Array)) (*mocks.MockBlockChain, database.Database) {
+	chain := mocks.NewMockBlockChain(gomock.NewController(t))
+	chain.EXPECT().CurrentBlock().Return(types.NewBlockWithHeader(&types.Header{Number: big.NewInt(2)})).AnyTimes()
+	chain.EXPECT().GetHeaderByNumber(uint64(1)).Return(header1)
+	chain.EXPECT().GetHeaderByNumber(uint64(9)).Return((*types.Header)(nil))
+
+	db := database.NewMemDB()
+	writeIndex(db, StoredUint64Array{1, 9})
+	return chain, db
+}
+
+// A stale block above head must be skipped, not panic, and the index is left untouched
+// (read stays pure).
+func TestReadGovDataFromDBSkipsStaleBlock(t *testing.T) {
+	gov1 := headergov.NewGovData(gov.PartialParamSet{gov.GovernanceUnitPrice: uint64(100)})
+	govBytes, err := gov1.ToGovBytes()
+	require.NoError(t, err)
+
+	chain, db := mockChainWithStaleBlock(t, &types.Header{Governance: govBytes}, WriteGovDataBlockNums)
+	assert.Equal(t, map[uint64]headergov.GovData{1: gov1}, readGovDataFromDB(chain, db))
+	assert.Equal(t, StoredUint64Array{1, 9}, ReadGovDataBlockNums(db))
+}
+
+func TestReadVoteDataFromDBSkipsStaleBlock(t *testing.T) {
+	vote1 := headergov.NewVoteData(common.Address{1}, string(gov.GovernanceUnitPrice), uint64(100))
+	voteBytes, err := vote1.ToVoteBytes()
+	require.NoError(t, err)
+
+	chain, db := mockChainWithStaleBlock(t, &types.Header{Vote: voteBytes}, WriteVoteDataBlockNums)
+	assert.Equal(t, map[uint64]headergov.VoteData{1: vote1}, readVoteDataFromDB(chain, db))
+	assert.Equal(t, StoredUint64Array{1, 9}, ReadVoteDataBlockNums(db))
+}
+
 func TestInitialDB(t *testing.T) {
 	config := getTestChainConfig()
 
```

### node/cn/api_backend_test.go
```diff
@@ -185,8 +185,9 @@ func TestCNAPIBackend_SetHead(t *testing.T) {
 	mockCtrl, mockBlockChain, _, api := newCNAPIBackend(t)
 	defer mockCtrl.Finish()
 
-	// headergov.Init reads genesis block
+	// headergov.Init reads genesis block and the current head
 	mockBlockChain.EXPECT().GetHeaderByNumber(uint64(0)).Return(&types.Header{}).Times(1)
+	mockBlockChain.EXPECT().CurrentBlock().Return(types.NewBlockWithHeader(&types.Header{Number: common.Big0})).AnyTimes()
 
 	mockDownloader := mocks2.NewMockProtocolManagerDownloader(mockCtrl)
 	mockDownloader.EXPECT().Cancel().Times(1)
```
