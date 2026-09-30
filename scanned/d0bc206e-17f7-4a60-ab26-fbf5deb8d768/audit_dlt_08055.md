# [?] trie: fix overflow in write cache parent tracking (#18165)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-11-22
Source: https://github.com/celo-org/celo-blockchain/commit/2843001ac218040f7e773159596625654f4e4148
Type: security-commit

## Details
trie: fix overflow in write cache parent tracking (#18165)

trie/database: fix overflow in parent tracking

## Patch
### trie/database.go
```diff
@@ -141,7 +141,7 @@ type cachedNode struct {
 	node node   // Cached collapsed trie node, or raw rlp data
 	size uint16 // Byte size of the useful cached data
 
-	parents  uint16                 // Number of live nodes referencing this one
+	parents  uint32                 // Number of live nodes referencing this one
 	children map[common.Hash]uint16 // External children referenced by this node
 
 	flushPrev common.Hash // Previous node in the flush-list
```
