# [?] fix: fast node can not recover from force kill or panic (#1014)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2022-07-25
Source: https://github.com/bnb-chain/bsc/commit/0ed265c5e0a75fbf12d30dc7642c025e68d7cfbf
Type: security-commit

## Details
fix: fast node can not recover from force kill or panic (#1014)

## Patch
### core/blockchain_reader.go
```diff
@@ -258,6 +258,9 @@ func (bc *BlockChain) GetTd(hash common.Hash, number uint64) *big.Int {
 
 // HasState checks if state trie is fully present in the database or not.
 func (bc *BlockChain) HasState(hash common.Hash) bool {
+	if bc.stateCache.NoTries() {
+		return bc.snaps != nil && bc.snaps.Snapshot(hash) != nil
+	}
 	if bc.pipeCommit && bc.snaps != nil {
 		// If parent snap is pending on verification, treat it as state exist
 		if s := bc.snaps.Snapshot(hash); s != nil && !s.Verified() {
```
