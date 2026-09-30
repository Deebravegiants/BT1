# [?] fix race condition on preimage (#797)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2022-03-28
Source: https://github.com/bnb-chain/bsc/commit/5f1aabeb38a21bff9ffe25e1dd138b2b9d335007
Type: security-commit

## Details
fix race condition on preimage (#797)

## Patch
### trie/database.go
```diff
@@ -722,17 +722,18 @@ func (db *Database) Commit(node common.Hash, report bool, callback func(common.H
 	batch := db.diskdb.NewBatch()
 
 	// Move all of the accumulated preimages into a write batch
+	db.lock.RLock()
 	if db.preimages != nil {
 		rawdb.WritePreimages(batch, db.preimages)
 		// Since we're going to replay trie node writes into the clean cache, flush out
 		// any batched pre-images before continuing.
 		if err := batch.Write(); err != nil {
+			db.lock.RUnlock()
 			return err
 		}
 		batch.Reset()
 	}
 	// Move the trie itself into the batch, flushing if enough data is accumulated
-	db.lock.RLock()
 	nodes, storage := len(db.dirties), db.dirtiesSize
 	db.lock.RUnlock()
 
```
