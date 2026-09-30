# [?] Fix int overflow by int -> uint32 and uint64 conversion

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-11-06
Source: https://github.com/harmony-one/harmony/commit/e410b13c70338e9cc3acb0f8e9e554bcd332fd87
Type: security-commit

## Details
Fix int overflow by int -> uint32 and uint64 conversion

## Patch
### internal/hmyapi/transactionpool.go
```diff
@@ -24,8 +24,8 @@ var (
 // TxHistoryArgs is struct to make GetTransactionsHistory request
 type TxHistoryArgs struct {
 	Address   string `json:"address"`
-	PageIndex int    `json:"pageIndex"`
-	PageSize  int    `json:"pageSize"`
+	PageIndex uint32 `json:"pageIndex"`
+	PageSize  uint32 `json:"pageSize"`
 	FullTx    bool   `json:"fullTx"`
 	TxType    string `json:"txType"`
 	Order     string `json:"order"`
```

### internal/hmyapi/util.go
```diff
@@ -13,7 +13,7 @@ import (
 
 // defaultPageSize is to have default pagination.
 const (
-	defaultPageSize = 100
+	defaultPageSize = uint32(100)
 )
 
 // ReturnWithPagination returns result with pagination (offset, page in TxHistoryArgs).
@@ -23,10 +23,10 @@ func ReturnWithPagination(hashes []common.Hash, args TxHistoryArgs) []common.Has
 	if args.PageSize > 0 {
 		pageSize = args.PageSize
 	}
-	if pageIndex < 0 || pageSize*pageIndex >= len(hashes) {
+	if uint64(pageSize)*uint64(pageIndex) >= uint64(len(hashes)) {
 		return make([]common.Hash, 0)
 	}
-	if pageSize*pageIndex+pageSize > len(hashes) {
+	if uint64(pageSize)*uint64(pageIndex)+uint64(pageSize) > uint64(len(hashes)) {
 		return hashes[pageSize*pageIndex:]
 	}
 	return hashes[pageSize*pageIndex : pageSize*pageIndex+pageSize]
```
