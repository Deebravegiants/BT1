# [?] port the fix from go-ethereum for interface conversion panic (#2816)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-04-12
Source: https://github.com/harmony-one/harmony/commit/a732b52d8622d976f057ab1c09e617aa99ddd587
Type: security-commit

## Details
port the fix from go-ethereum for interface conversion panic (#2816)

## Patch
### core/blockchain.go
```diff
@@ -240,6 +240,9 @@ func NewBlockChain(
 	if bc.genesisBlock == nil {
 		return nil, ErrNoGenesis
 	}
+	var nilBlock *types.Block
+	bc.currentBlock.Store(nilBlock)
+	bc.currentFastBlock.Store(nilBlock)
 	if err := bc.loadLastState(); err != nil {
 		return nil, err
 	}
```
