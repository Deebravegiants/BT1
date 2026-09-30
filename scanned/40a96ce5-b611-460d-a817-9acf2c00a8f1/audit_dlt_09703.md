# [?] Fix panic in lyra2 when mining

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2023-09-24
Source: https://github.com/etclabscore/core-geth/commit/e3dfe6716db5d24a4a7e8f293d6027efd416b3ba
Type: security-commit

## Details
Fix panic in lyra2 when mining

## Patch
### consensus/lyra2/consensus.go
```diff
@@ -394,7 +394,7 @@ func (lyra2 *Lyra2) FinalizeAndAssemble(chain consensus.ChainHeaderReader, heade
 	header.Root = state.IntermediateRoot(chain.Config().IsEnabled(chain.Config().GetEIP161dTransition, header.Number))
 
 	// Header seems complete, assemble into a block and return
-	return types.NewBlock(header, txs, uncles, receipts, new(trie.Trie)), nil
+	return types.NewBlock(header, txs, uncles, receipts, trie.NewStackTrie(nil)), nil
 }
 
 // SealHash returns the hash of a block prior to it being sealed.
```
