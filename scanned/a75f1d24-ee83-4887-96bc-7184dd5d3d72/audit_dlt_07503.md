# [?] Fix nil panic if block is not found in database

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-09-10
Source: https://github.com/harmony-one/harmony/commit/2a7168a46baf14a06c06e3aa8abfad400221b820
Type: security-commit

## Details
Fix nil panic if block is not found in database

This could occur as a result of database corruption or database update
race, where transaction → (blockHash, blockNum, txIndex) lookup succeeds
but the body for blockHash is not (yet) in the database.

## Patch
### core/rawdb/accessors_indexes.go
```diff
@@ -71,6 +71,14 @@ func ReadTransaction(db DatabaseReader, hash common.Hash) (*types.Transaction, c
 		return nil, common.Hash{}, 0, 0
 	}
 	body := ReadBody(db, blockHash, blockNumber)
+	if body == nil {
+		utils.Logger().Error().
+			Uint64("number", blockNumber).
+			Str("hash", blockHash.Hex()).
+			Uint64("index", txIndex).
+			Msg("block Body referenced missing")
+		return nil, common.Hash{}, 0, 0
+	}
 	tx := body.TransactionAt(int(txIndex))
 	if tx == nil {
 		utils.Logger().Error().
```
