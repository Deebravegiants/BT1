# [?] trie: fix bloom crash on fast sync restart

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-02-16
Source: https://github.com/ethereum/go-ethereum/commit/e991bdae2458dbee5a28addd188a897858aa34dd
Type: security-commit

## Details
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
