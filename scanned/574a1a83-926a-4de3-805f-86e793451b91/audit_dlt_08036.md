# [?] core: fix crash in chain reimport (#19986)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-08-21
Source: https://github.com/celo-org/celo-blockchain/commit/4aee0d1994ad286c18aa3a586ae950e96979a7f1
Type: security-commit

## Details
core: fix crash in chain reimport (#19986)

* blockchain: fix flaw in block import

* core/blockchain: address review concerns

* core/blockchain: go format with 's'

## Patch
### core/blockchain.go
```diff
@@ -1742,6 +1742,11 @@ func (bc *BlockChain) insertSideChain(block *types.Block, it *insertIterator) (i
 			canonical := bc.GetBlockByNumber(number)
 			if canonical != nil && canonical.Hash() == block.Hash() {
 				// Not a sidechain block, this is a re-import of a canon block which has it's state pruned
+
+				// Collect the TD of the block. Since we know it's a canon one,
+				// we can get it directly, and not (like further below) use
+				// the parent and then add the block on top
+				externTd = bc.GetTd(block.Hash(), block.NumberU64())
 				continue
 			}
 			if canonical != nil && canonical.Root() == block.Root() {
```

### core/blockchain_test.go
```diff
@@ -2241,3 +2241,49 @@ func BenchmarkBlockChain_1x1000Executions(b *testing.B) {
 	}
 	benchmarkLargeNumberOfValueToNonexisting(b, numTxs, numBlocks, recipientFn, dataFn)
 }
+
+// Tests that importing a some old blocks, where all blocks are before the
+// pruning point.
+// This internally leads to a sidechain import, since the blocks trigger an
+// ErrPrunedAncestor error.
+// This may e.g. happen if
+//   1. Downloader rollbacks a batch of inserted blocks and exits
+//   2. Downloader starts to sync again
+//   3. The blocks fetched are all known and canonical blocks
+func TestSideImportPrunedBlocks(t *testing.T) {
+	// Generate a canonical chain to act as the main dataset
+	engine := ethash.NewFaker()
+	db := rawdb.NewMemoryDatabase()
+	genesis := new(Genesis).MustCommit(db)
+
+	// Generate and import the canonical chain
+	blocks, _ := GenerateChain(params.TestChainConfig, genesis, engine, db, 2*TriesInMemory, nil)
+	diskdb := rawdb.NewMemoryDatabase()
+	new(Genesis).MustCommit(diskdb)
+	chain, err := NewBlockChain(diskdb, nil, params.TestChainConfig, engine, vm.Config{}, nil)
+	if err != nil {
+		t.Fatalf("failed to create tester chain: %v", err)
+	}
+	if n, err := chain.InsertChain(blocks); err != nil {
+		t.Fatalf("block %d: failed to insert into chain: %v", n, err)
+	}
+
+	lastPrunedIndex := len(blocks) - TriesInMemory - 1
+	lastPrunedBlock := blocks[lastPrunedIndex]
+
+	// Verify pruning of lastPrunedBlock
+	if chain.HasBlockAndState(lastPrunedBlock.Hash(), lastPrunedBlock.NumberU64()) {
+		t.Errorf("Block %d not pruned", lastPrunedBlock.NumberU64())
+	}
+	firstNonPrunedBlock := blocks[len(blocks)-TriesInMemory]
+	// Verify firstNonPrunedBlock is not pruned
+	if !chain.HasBlockAndState(firstNonPrunedBlock.Hash(), firstNonPrunedBlock.NumberU64()) {
+		t.Errorf("Block %d pruned", firstNonPrunedBlock.NumberU64())
+	}
+	// Now re-import some old blocks
+	blockToReimport := blocks[5:8]
+	_, err = chain.InsertChain(blockToReimport)
+	if err != nil {
+		t.Errorf("Got error, %v", err)
+	}
+}
```
