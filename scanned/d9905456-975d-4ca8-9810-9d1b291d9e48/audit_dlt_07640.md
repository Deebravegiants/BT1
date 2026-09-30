# [?] core: fix missing receipt on Clique crashes (#21045)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2020-05-13
Source: https://github.com/ethereum/go-ethereum/commit/d02301f758df1d16875c959b58cf91c76edecbdd
Type: security-commit

## Details
core: fix missing receipt on Clique crashes (#21045)

* core: fix missing receipt

* core: address comment

## Patch
### core/blockchain.go
```diff
@@ -1731,6 +1731,20 @@ func (bc *BlockChain) insertChain(chain types.Blocks, verifySeals bool) (int, er
 				"uncles", len(block.Uncles()), "txs", len(block.Transactions()), "gas", block.GasUsed(),
 				"root", block.Root())
 
+			// Special case. Commit the empty receipt slice if we meet the known
+			// block in the middle. It can only happen in the clique chain. Whenever
+			// we insert blocks via `insertSideChain`, we only commit `td`, `header`
+			// and `body` if it's non-existent. Since we don't have receipts without
+			// reexecution, so nothing to commit. But if the sidechain will be adpoted
+			// as the canonical chain eventually, it needs to be reexecuted for missing
+			// state, but if it's this special case here(skip reexecution) we will lose
+			// the empty receipt entry.
+			if len(block.Transactions()) == 0 {
+				rawdb.WriteReceipts(bc.db, block.Hash(), block.NumberU64(), nil)
+			} else {
+				log.Error("Please file an issue, skip known block execution without receipt",
+					"hash", block.Hash(), "number", block.NumberU64())
+			}
 			if err := bc.writeKnownBlock(block); err != nil {
 				return it.index, err
 			}
```
