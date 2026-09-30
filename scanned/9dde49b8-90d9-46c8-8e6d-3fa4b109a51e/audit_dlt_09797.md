# [?] Fixed data race. (#4686)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2024-07-19
Source: https://github.com/harmony-one/harmony/commit/a65cf7175dc708144aacdecaaa6bb725a9f4f3f9
Type: security-commit

## Details
Fixed data race. (#4686)

## Patch
### core/blockchain_impl.go
```diff
@@ -490,6 +490,9 @@ func (bc *BlockChainImpl) ValidateNewBlock(block *types.Block, beaconChain Block
 	if block.NumberU64() <= bc.CurrentBlock().NumberU64() {
 		return errors.Errorf("block with the same block number is already committed: %d", block.NumberU64())
 	}
+
+	bc.chainmu.Lock()
+	defer bc.chainmu.Unlock()
 	if err := bc.validator.ValidateHeader(block, true); err != nil {
 		utils.Logger().Error().
 			Str("blockHash", block.Hash().Hex()).
```
