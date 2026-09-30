# [?] Fix for overflow in parent tracking (cherrypicking go-ethereum#18165 pull) (#876)

## Summary
Severity: Unknown
Chain: Quorum
Component: Consensys-inc-archive/quorum
Published: 2019-11-13
Source: https://github.com/Consensys-inc-archive/quorum/commit/f80914446a3110da8f8fbf3f91a65ed521cca278
Type: security-commit

## Details
Fix for overflow in parent tracking (cherrypicking go-ethereum#18165 pull) (#876)

## Patch
### trie/database.go
```diff
@@ -134,7 +134,7 @@ type cachedNode struct {
 	node node   // Cached collapsed trie node, or raw rlp data
 	size uint16 // Byte size of the useful cached data
 
-	parents  uint16                 // Number of live nodes referencing this one
+	parents  uint32                 // Number of live nodes referencing this one
 	children map[common.Hash]uint16 // External children referenced by this node
 
 	flushPrev common.Hash // Previous node in the flush-list
```
