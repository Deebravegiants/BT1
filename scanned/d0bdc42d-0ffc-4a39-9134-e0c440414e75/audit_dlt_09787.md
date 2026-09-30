# [?] fix: resolve eviction off-by-one, data race on stats, and double-Stop panic in block number cache

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2026-02-16
Source: https://github.com/harmony-one/harmony/commit/1ae02cf0d07de463d5338608c44c47714fd5a546
Type: security-commit

## Details
fix: resolve eviction off-by-one, data race on stats, and double-Stop panic in block number cache

## Patch
### api/service/synchronize/stagedstreamsync/block_number_cache.go
```diff
@@ -39,6 +39,7 @@ type BlockNumberCache struct {
 	cleanupTicker *time.Ticker
 	stats         CacheStats
 	stopChan      chan struct{}
+	stopOnce      sync.Once
 }
 
 // ProtocolProvider defines interface to get block number
@@ -169,14 +170,14 @@ func (c *BlockNumberCache) doGetCurrentNumberRequest(ctx context.Context) (uint6
 }
 
 // evictOldestEntries removes the oldest entries to make room for new ones
-// Only removes the minimum number of entries needed to get under MaxSize
+// Ensures at least one slot is available after eviction
 func (c *BlockNumberCache) evictOldestEntries() {
-	if len(c.cache) <= c.config.MaxSize {
+	if len(c.cache) < c.config.MaxSize {
 		return
 	}
 
-	// Calculate how many entries to remove
-	entriesToRemove := len(c.cache) - c.config.MaxSize
+	// Calculate how many entries to remove (at least 1 to make room for new entry)
+	entriesToRemove := len(c.cache) - c.config.MaxSize + 1
 
 	// Create a slice of entries with their timestamps for sorting
 	type entryWithTime struct {
@@ -207,7 +208,6 @@ func (c *BlockNumberCache) backgroundCleanup() {
 		select {
 		case <-c.cleanupTicker.C:
 			c.cleanupExpiredEntries()
-			c.stats.LastCleanup = time.Now()
 		case <-c.stopChan:
 			c.cleanupTicker.Stop()
 			return
@@ -236,6 +236,7 @@ func (c *BlockNumberCache) cleanupExpiredEntries() {
 	if expiredCount > 0 {
 		c.stats.Evictions += uint64(expiredCount)
 	}
+	c.stats.LastCleanup = time.Now()
 }
 
 // GetStats returns current cache statistics
@@ -300,7 +301,9 @@ func (c *BlockNumberCache) Reset() {
 
 // Stop stops the background cleanup goroutine
 func (c *BlockNumberCache) Stop() {
-	close(c.stopChan)
+	c.stopOnce.Do(func() {
+		close(c.stopChan)
+	})
 }
 
 // updateAccessStats updates the access statistics for a stream
```
