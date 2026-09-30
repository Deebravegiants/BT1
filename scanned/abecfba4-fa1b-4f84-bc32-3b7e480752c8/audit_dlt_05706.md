# [?] graphdb: fix potential sql tx exhaustion

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-12-07
Source: https://github.com/lightningnetwork/lnd/commit/2d25bce1bf69e9ad4bdcfef5b4114f24b90ee63c
Type: security-commit

## Details
graphdb: fix potential sql tx exhaustion

We should avoid taking the lock of a mutex inside transaction.
Currently we also take this lock in other places and there is a
chance that in case the application lock aquires the lock but
all transactions are already blocked waiting for the mutex to
unlock, we end up in a deadlock.

## Patch
### graph/db/kv_store.go
```diff
@@ -2108,6 +2108,13 @@ func (c *KVStore) fetchNextChanUpdateBatch(
 		batch   []ChannelEdge
 		hasMore bool
 	)
+
+	// Acquire read lock before starting transaction to ensure
+	// consistent lock ordering (cacheMu -> DB) and prevent
+	// deadlock with write operations.
+	c.cacheMu.RLock()
+	defer c.cacheMu.RUnlock()
+
 	err := kvdb.View(c.db, func(tx kvdb.RTx) error {
 		edges := tx.ReadBucket(edgeBucket)
 		if edges == nil {
@@ -2187,9 +2194,7 @@ func (c *KVStore) fetchNextChanUpdateBatch(
 				continue
 			}
 
-			// Before we read the edge info, we'll see if this
-			// element is already in the cache or not.
-			c.cacheMu.RLock()
+			// Check cache (we already hold shared read lock).
 			if channel, ok := c.chanCache.get(chanIDInt); ok {
 				state.edgesSeen[chanIDInt] = struct{}{}
 
@@ -2200,11 +2205,8 @@ func (c *KVStore) fetchNextChanUpdateBatch(
 
 				indexKey, _ = updateCursor.Next()
 
-				c.cacheMu.RUnlock()
-
 				continue
 			}
-			c.cacheMu.RUnlock()
 
 			// The edge wasn't in the cache, so we'll fetch it along
 			// w/ the edge policies and nodes.
```

### graph/db/sql_store.go
```diff
@@ -1127,6 +1127,11 @@ func (s *SQLStore) ChanUpdatesInHorizon(startTime, endTime time.Time,
 		for hasMore {
 			var batch []ChannelEdge
 
+			// Acquire read lock before starting transaction to
+			// ensure consistent lock ordering (cacheMu -> DB) and
+			// prevent deadlock with write operations.
+			s.cacheMu.RLock()
+
 			err := s.db.ExecTx(ctx, sqldb.ReadTxOpt(),
 				func(db SQLQueries) error {
 					//nolint:ll
@@ -1179,11 +1184,11 @@ func (s *SQLStore) ChanUpdatesInHorizon(startTime, endTime time.Time,
 							continue
 						}
 
-						s.cacheMu.RLock()
+						// Check cache (we already hold
+						// shared read lock).
 						channel, ok := s.chanCache.get(
 							chanIDInt,
 						)
-						s.cacheMu.RUnlock()
 						if ok {
 							hits++
 							total++
@@ -1217,6 +1222,9 @@ func (s *SQLStore) ChanUpdatesInHorizon(startTime, endTime time.Time,
 					)
 				})
 
+			// Release read lock after transaction completes.
+			s.cacheMu.RUnlock()
+
 			if err != nil {
 				log.Errorf("ChanUpdatesInHorizon "+
 					"batch error: %v", err)
```
