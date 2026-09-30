# [?] fix deadlock in FindRetentionBound

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/go-ethereum
Published: 2022-08-30
Source: https://github.com/OffchainLabs/go-ethereum/commit/57a6751e61085828edf859dbf396c5b5e3feafff
Type: security-commit

## Details
fix deadlock in FindRetentionBound

## Patch
### core/blockchain_arbitrum.go
```diff
@@ -92,7 +92,7 @@ func (bc *BlockChain) FindRetentionBound() uint64 {
 	//
 	a := timeBound   // a prunable block, if possible
 	b := heightBound // not prunable
-	for a+1 < b {
+	for a+2 < b {
 		mid := a/2 + b/2 // a < mid < b
 		age := current.Time() - bc.GetBlockByNumber(mid).Time()
 		if age <= minimumAge {
```
