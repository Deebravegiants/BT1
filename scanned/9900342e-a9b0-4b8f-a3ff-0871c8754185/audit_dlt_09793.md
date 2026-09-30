# [?] Fix nil trie panic in getDeletedStateObject

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2025-12-19
Source: https://github.com/harmony-one/harmony/commit/069d68a47d199228675878e2f4e12cb836c74f33
Type: security-commit

## Details
Fix nil trie panic in getDeletedStateObject

## Patch
### core/state/statedb.go
```diff
@@ -639,6 +639,9 @@ func (db *DB) getDeletedStateObject(addr common.Address) *Object {
 	}
 	// If snapshot unavailable or reading from it failed, load from the database
 	if data == nil {
+		if db.trie == nil {
+			return nil
+		}
 		start := time.Now()
 		var err error
 		data, err = db.trie.TryGetAccount(addr)
```
