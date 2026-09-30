# [?] Fix security overflow issue

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-11-05
Source: https://github.com/harmony-one/harmony/commit/56d8be156260e1d10f1f310ac50bd8f56b5a2642
Type: security-commit

## Details
Fix security overflow issue

## Patch
### internal/hmyapi/util.go
```diff
@@ -23,7 +23,7 @@ func ReturnWithPagination(hashes []common.Hash, args TxHistoryArgs) []common.Has
 	if args.PageSize > 0 {
 		pageSize = args.PageSize
 	}
-	if pageSize*pageIndex >= len(hashes) {
+	if pageIndex < 0 || pageSize*pageIndex >= len(hashes) {
 		return make([]common.Hash, 0)
 	}
 	if pageSize*pageIndex+pageSize > len(hashes) {
```
