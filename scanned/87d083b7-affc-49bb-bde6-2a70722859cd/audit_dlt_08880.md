# [?] fix(trie): minor fix for the trie panic (#3344)

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2026-01-02
Source: https://github.com/NethermindEth/juno/commit/a50928a9a52a6b53ab7021d23495c6350f9d4e4a
Type: security-commit

## Details
fix(trie): minor fix for the trie panic (#3344)

minor fix for the trie panic

## Patch
### core/trie/trie.go
```diff
@@ -791,8 +791,13 @@ func (t *Trie) Hash() (felt.Felt, error) {
 	}
 
 	storage := t.storage
-	t.storage = storage.SyncedStorage()
-	defer func() { t.storage = storage }()
+	syncedStorage := storage.SyncedStorage()
+	t.storage = syncedStorage
+	t.readStorage = syncedStorage.ReadStorage
+	defer func() {
+		t.storage = storage
+		t.readStorage = storage.ReadStorage
+	}()
 	root, err := t.updateValueIfDirty(t.rootKey)
 	if err != nil {
 		return felt.Zero, err
```
