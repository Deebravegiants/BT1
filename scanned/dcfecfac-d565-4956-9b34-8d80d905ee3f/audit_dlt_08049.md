# [?] core: fix pruner panic when importing low-diff-large-sidechain

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-02-08
Source: https://github.com/celo-org/celo-blockchain/commit/4da209290831720b0f61754b92dabefd5cb35b6d
Type: security-commit

## Details
core: fix pruner panic when importing low-diff-large-sidechain

## Patch
### core/blockchain.go
```diff
@@ -972,20 +972,26 @@ func (bc *BlockChain) WriteBlockWithState(block *types.Block, receipts []*types.
 				triedb.Cap(limit - ethdb.IdealBatchSize)
 			}
 			// Find the next state trie we need to commit
-			header := bc.GetHeaderByNumber(current - triesInMemory)
-			chosen := header.Number.Uint64()
+			chosen := current - triesInMemory
 
 			// If we exceeded out time allowance, flush an entire trie to disk
 			if bc.gcproc > bc.cacheConfig.TrieTimeLimit {
-				// If we're exceeding limits but haven't reached a large enough memory gap,
-				// warn the user that the system is becoming unstable.
-				if chosen < lastWrite+triesInMemory && bc.gcproc >= 2*bc.cacheConfig.TrieTimeLimit {
-					log.Info("State in memory for too long, committing", "time", bc.gcproc, "allowance", bc.cacheConfig.TrieTimeLimit, "optimum", float64(chosen-lastWrite)/triesInMemory)
+				// If the header is missing (canonical chain behind), we're reorging a low
+				// diff sidechain. Suspend committing until this operation is completed.
+				header := bc.GetHeaderByNumber(chosen)
+				if header == nil {
+					log.Warn("Reorg in progress, trie commit postponed", "number", chosen)
+				} else {
+					// If we're exceeding limits but haven't reached a large enough memory gap,
+					// warn the user that the system is becoming unstable.
+					if chosen < lastWrite+triesInMemory && bc.gcproc >= 2*bc.cacheConfig.TrieTimeLimit {
+						log.Info("State in memory for too long, committing", "time", bc.gcproc, "allowance", bc.cacheConfig.TrieTimeLimit, "optimum", float64(chosen-lastWrite)/triesInMemory)
+					}
+					// Flush an entire trie and restart the counters
+					triedb.Commit(header.Root, true)
+					lastWrite = chosen
+					bc.gcproc = 0
 				}
-				// Flush an entire trie and restart the counters
-				triedb.Commit(header.Root, true)
-				lastWrite = chosen
-				bc.gcproc = 0
 			}
 			// Garbage collect anything below our required write retention
 			for !bc.triegc.Empty() {
@@ -1317,7 +1323,7 @@ func (bc *BlockChain) insertSidechain(block *types.Block, it *insertIterator) (i
 			if err := bc.WriteBlockWithoutState(block, externTd); err != nil {
 				return it.index, nil, nil, err
 			}
-			log.Debug("Inserted sidechain block", "number", block.Number(), "hash", block.Hash(),
+			log.Debug("Injected sidechain block", "number", block.Number(), "hash", block.Hash(),
 				"diff", block.Difficulty(), "elapsed", common.PrettyDuration(time.Since(start)),
 				"txs", len(block.Transactions()), "gas", block.GasUsed(), "uncles", len(block.Uncles()),
 				"root", block.Root())
```

### core/blockchain_test.go
```diff
@@ -1487,16 +1487,22 @@ func BenchmarkBlockChain_1x1000Executions(b *testing.B) {
 // Tests that importing a very large side fork, which is larger than the canon chain,
 // but where the difficulty per block is kept low: this means that it will not
 // overtake the 'canon' chain until after it's passed canon by about 200 blocks.
-func TestLargeOldSidechainWithALowTdChain(t *testing.T) {
-
+//
+// Details at:
+//  - https://github.com/ethereum/go-ethereum/issues/18977
+//  - https://github.com/ethereum/go-ethereum/pull/18988
+func TestLowDiffLongChain(t *testing.T) {
 	// Generate a canonical chain to act as the main dataset
 	engine := ethash.NewFaker()
-
 	db := ethdb.NewMemDatabase()
 	genesis := new(Genesis).MustCommit(db)
-	// We must use a pretty long chain to ensure that the fork
-	// doesn't overtake us until after at least 128 blocks post tip
-	blocks, _ := generateChain(params.TestChainConfig, genesis, engine, db, 6*triesInMemory, func(i int, b *BlockGen) { b.SetCoinbase(common.Address{1}) }, makeHeaderWithLargeDifficulty)
+
+	// We must use a pretty long chain to ensure that the fork doesn't overtake us
+	// until after at least 128 blocks post tip
+	blocks, _ := GenerateChain(params.TestChainConfig, genesis, engine, db, 6*triesInMemory, func(i int, b *BlockGen) {
+		b.SetCoinbase(common.Address{1})
+		b.OffsetTime(-9)
+	})
 
 	// Import the canonical chain
 	diskdb := ethdb.NewMemDatabase()
@@ -1506,19 +1512,14 @@ func TestLargeOldSidechainWithALowTdChain(t *testing.T) {
 	if err != nil {
 		t.Fatalf("failed to create tester chain: %v", err)
 	}
-	for i := 0; i < len(blocks); i++ {
-		if _, err := chain.InsertChain(blocks[i : i+1]); err != nil {
-			t.Fatalf("block %d: failed to insert into chain: %v", i, err)
-		}
+	if n, err := chain.InsertChain(blocks); err != nil {
+		t.Fatalf("block %d: failed to insert into chain: %v", n, err)
 	}
-	// Dereference all the recent tries and ensure no past trie is left in
-	for i := 0; i < triesInMemory; i++ {
-		chain.stateCache.TrieDB().Dereference(blocks[len(blocks)-1-i].Root())
-	}
-
 	// Generate fork chain, starting from an early block
 	parent := blocks[10]
-	fork, _ := generateChain(params.TestChainConfig, parent, engine, db, 256+6*triesInMemory, func(i int, b *BlockGen) { b.SetCoinbase(common.Address{2}) }, makeHeaderWithSmallDifficulty)
+	fork, _ := GenerateChain(params.TestChainConfig, parent, engine, db, 8*triesInMemory, func(i int, b *BlockGen) {
+		b.SetCoinbase(common.Address{2})
+	})
 
 	// And now import the fork
 	if i, err := chain.InsertChain(fork); err != nil {
@@ -1528,6 +1529,12 @@ func TestLargeOldSidechainWithALowTdChain(t *testing.T) {
 	if got := fork[len(fork)-1].Hash(); got != head.Hash() {
 		t.Fatalf("head wrong, expected %x got %x", head.Hash(), got)
 	}
-	td := chain.GetTd(head.Hash(), head.NumberU64())
-	fmt.Printf("td %v", td)
+	// Sanity check that all the canonical numbers are present
+	header := chain.CurrentHeader()
+	for number := head.NumberU64(); number > 0; number-- {
+		if hash := chain.GetHeaderByNumber(number).Hash(); hash != header.Hash() {
+			t.Fatalf("header %d: canonical hash mismatch: have %x, want %x", number, hash, header.Hash())
+		}
+		header = chain.GetHeader(header.ParentHash, number-1)
+	}
 }
```

### core/chain_makers.go
```diff
@@ -48,8 +48,6 @@ type BlockGen struct {
 	engine consensus.Engine
 }
 
-type headerGenFn func(chain consensus.ChainReader, parent *types.Block, state *state.StateDB, engine consensus.Engine) *types.Header
-
 // SetCoinbase sets the coinbase of the generated block.
 // It can be called at most once.
 func (b *BlockGen) SetCoinbase(addr common.Address) {
@@ -151,7 +149,7 @@ func (b *BlockGen) PrevBlock(index int) *types.Block {
 // associated difficulty. It's useful to test scenarios where forking is not
 // tied to chain length directly.
 func (b *BlockGen) OffsetTime(seconds int64) {
-	b.header.Time.Add(b.header.Time, new(big.Int).SetInt64(seconds))
+	b.header.Time.Add(b.header.Time, big.NewInt(seconds))
 	if b.header.Time.Cmp(b.parent.Header().Time) <= 0 {
 		panic("block time out of range")
 	}
@@ -172,19 +170,14 @@ func (b *BlockGen) OffsetTime(seconds int64) {
 // values. Inserting them into BlockChain requires use of FakePow or
 // a similar non-validating proof of work implementation.
 func GenerateChain(config *params.ChainConfig, parent *types.Block, engine consensus.Engine, db ethdb.Database, n int, gen func(int, *BlockGen)) ([]*types.Block, []types.Receipts) {
-	return generateChain(config, parent, engine, db, n, gen, makeHeader)
-}
-
-func generateChain(config *params.ChainConfig, parent *types.Block, engine consensus.Engine, db ethdb.Database, n int, gen func(int, *BlockGen), headerGen headerGenFn) ([]*types.Block, []types.Receipts) {
 	if config == nil {
 		config = params.TestChainConfig
 	}
 	blocks, receipts := make(types.Blocks, n), make([]types.Receipts, n)
 	chainreader := &fakeChainReader{config: config}
 	genblock := func(i int, parent *types.Block, statedb *state.StateDB) (*types.Block, types.Receipts) {
 		b := &BlockGen{i: i, chain: blocks, parent: parent, statedb: statedb, config: config, engine: engine}
-		//b.header = makeHeader(chainreader, parent, statedb, b.engine)
-		b.header = headerGen(chainreader, parent, statedb, b.engine)
+		b.header = makeHeader(chainreader, parent, statedb, b.engine)
 
 		// Mutate the state and block according to any hard-fork specs
 		if daoBlock := config.DAOForkBlock; daoBlock != nil {
@@ -255,54 +248,6 @@ func makeHeader(chain consensus.ChainReader, parent *types.Block, state *state.S
 	}
 }
 
-func makeHeaderWithLargeDifficulty(chain consensus.ChainReader, parent *types.Block, state *state.StateDB, engine consensus.Engine) *types.Header {
-	var time *big.Int
-	if parent.Time() == nil {
-		time = big.NewInt(1)
-	} else {
-		time = new(big.Int).Add(parent.Time(), big.NewInt(1)) // block time is fixed at 10 seconds
-	}
-
-	return &types.Header{
-		Root:       state.IntermediateRoot(chain.Config().IsEIP158(parent.Number())),
-		ParentHash: parent.Hash(),
-		Coinbase:   parent.Coinbase(),
-		Difficulty: engine.CalcDifficulty(chain, time.Uint64(), &types.Header{
-			Number:     parent.Number(),
-			Time:       new(big.Int).Sub(time, big.NewInt(1)),
-			Difficulty: parent.Difficulty(),
-			UncleHash:  parent.UncleHash(),
-		}),
-		GasLimit: CalcGasLimit(parent, parent.GasLimit(), parent.GasLimit()),
-		Number:   new(big.Int).Add(parent.Number(), common.Big1),
-		Time:     time,
-	}
-}
-
-func makeHeaderWithSmallDifficulty(chain consensus.ChainReader, parent *types.Block, state *state.StateDB, engine consensus.Engine) *types.Header {
-	var time *big.Int
-	if parent.Time() == nil {
-		time = big.NewInt(30)
-	} else {
-		time = new(big.Int).Add(parent.Time(), big.NewInt(30)) // block time is fixed at 10 seconds
-	}
-
-	return &types.Header{
-		Root:       state.IntermediateRoot(chain.Config().IsEIP158(parent.Number())),
-		ParentHash: parent.Hash(),
-		Coinbase:   parent.Coinbase(),
-		Difficulty: engine.CalcDifficulty(chain, time.Uint64(), &types.Header{
-			Number:     parent.Number(),
-			Time:       new(big.Int).Sub(time, big.NewInt(30)),
-			Difficulty: parent.Difficulty(),
-			UncleHash:  parent.UncleHash(),
-		}),
-		GasLimit: CalcGasLimit(parent, parent.GasLimit(), parent.GasLimit()),
-		Number:   new(big.Int).Add(parent.Number(), common.Big1),
-		Time:     time,
-	}
-}
-
 // makeHeaderChain creates a deterministic chain of headers rooted at parent.
 func makeHeaderChain(parent *types.Header, n int, engine consensus.Engine, db ethdb.Database, seed int) []*types.Header {
 	blocks := makeBlockChain(types.NewBlockWithHeader(parent), n, engine, db, seed)
```
