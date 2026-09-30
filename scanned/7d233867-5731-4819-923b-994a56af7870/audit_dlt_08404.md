# [?] fix(store/v1): Do not panic on prune in `Commit` (#18897)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-12-27
Source: https://github.com/cosmos/cosmos-sdk/commit/f08c8cce316dce33de32dc741bae081cab9b6823
Type: security-commit

## Details
fix(store/v1): Do not panic on prune in `Commit` (#18897)

## Patch
### store/rootmulti/store.go
```diff
@@ -496,7 +496,10 @@ func (rs *Store) Commit() types.CommitID {
 	rs.removalMap = make(map[types.StoreKey]bool)
 
 	if err := rs.handlePruning(version); err != nil {
-		panic(err)
+		rs.logger.Error(
+			"failed to prune store, please check your pruning configuration",
+			"err", err,
+		)
 	}
 
 	return types.CommitID{
```
