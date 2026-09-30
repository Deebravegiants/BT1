# [?] triedb/pathdb: fix panic in recoverable (#29107)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2024-02-28
Source: https://github.com/ethereum/go-ethereum/commit/5bae14f9df498243091078fc8d3ea6ab99669087
Type: security-commit

## Details
triedb/pathdb: fix panic in recoverable (#29107)

* triedb/pathdb: fix panic in recoverable

* triedb/pathdb: add todo

* triedb/pathdb: rename

* triedb/pathdb: rename

## Patch
### triedb/pathdb/database.go
```diff
@@ -391,17 +391,23 @@ func (db *Database) Recoverable(root common.Hash) bool {
 	if *id >= dl.stateID() {
 		return false
 	}
+	// This is a temporary workaround for the unavailability of the freezer in
+	// dev mode. As a consequence, the Pathdb loses the ability for deep reorg
+	// in certain cases.
+	// TODO(rjl493456442): Implement the in-memory ancient store.
+	if db.freezer == nil {
+		return false
+	}
 	// Ensure the requested state is a canonical state and all state
 	// histories in range [id+1, disklayer.ID] are present and complete.
-	parent := root
 	return checkHistories(db.freezer, *id+1, dl.stateID()-*id, func(m *meta) error {
-		if m.parent != parent {
+		if m.parent != root {
 			return errors.New("unexpected state history")
 		}
 		if len(m.incomplete) > 0 {
 			return errors.New("incomplete state history")
 		}
-		parent = m.root
+		root = m.root
 		return nil
 	}) == nil
 }
```
