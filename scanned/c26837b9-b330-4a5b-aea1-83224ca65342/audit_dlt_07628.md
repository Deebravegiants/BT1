# [?] Merge pull request #22332 from karalabe/fix-fastsync-restart-bloom-crash

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-02-16
Source: https://github.com/ethereum/go-ethereum/commit/915c614959024940515e044b2ea9c07317ce4b4a
Type: security-commit

## Details
Merge pull request #22332 from karalabe/fix-fastsync-restart-bloom-crash

trie: fix bloom crash on fast sync restart

## Patch
### trie/sync.go
```diff
@@ -313,11 +313,15 @@ func (s *Sync) Commit(dbw ethdb.Batch) error {
 	// Dump the membatch into a database dbw
 	for key, value := range s.membatch.nodes {
 		rawdb.WriteTrieNode(dbw, key, value)
-		s.bloom.Add(key[:])
+		if s.bloom != nil {
+			s.bloom.Add(key[:])
+		}
 	}
 	for key, value := range s.membatch.codes {
 		rawdb.WriteCode(dbw, key, value)
-		s.bloom.Add(key[:])
+		if s.bloom != nil {
+			s.bloom.Add(key[:])
+		}
 	}
 	// Drop the membatch data and return
 	s.membatch = newSyncMemBatch()
```
