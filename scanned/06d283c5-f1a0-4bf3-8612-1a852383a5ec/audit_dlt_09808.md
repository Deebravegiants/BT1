# [?] fix: panic if TriesInMemory is 1 to 2

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2023-02-10
Source: https://github.com/harmony-one/harmony/commit/b51be8bea3dfd9d0a0897c99dc562b857e30593a
Type: security-commit

## Details
fix: panic if TriesInMemory is 1 to 2

## Patch
### cmd/harmony/flags.go
```diff
@@ -408,8 +408,8 @@ func applyGeneralFlags(cmd *cobra.Command, config *harmonyconfig.HarmonyConfig)
 
 	if cli.IsFlagChanged(cmd, triesInMemoryFlag) {
 		value := cli.GetIntFlagValue(cmd, triesInMemoryFlag)
-		if value <= 1 {
-			panic("Must number greater than 1 for txpool.accountslots")
+		if value <= 2 {
+			panic("Must provide number greater than 2 for General.TriesInMemory")
 		}
 		config.General.TriesInMemory = value
 	}
```

### core/blockchain_impl.go
```diff
@@ -1071,7 +1071,7 @@ func (bc *BlockChainImpl) Stop() {
 	// We're writing three different states to catch different restart scenarios:
 	//  - HEAD:     So we don't need to reprocess any blocks in the general case
 	//  - HEAD-1:   So we don't do large reorgs if our HEAD becomes an uncle
-	//  - HEAD-127: So we have a hard limit on the number of blocks reexecuted
+	//  - HEAD-TriesInMemory: So we have a configurable hard limit on the number of blocks reexecuted (default 128)
 	if !bc.cacheConfig.Disabled {
 		triedb := bc.stateCache.TrieDB()
 
```
