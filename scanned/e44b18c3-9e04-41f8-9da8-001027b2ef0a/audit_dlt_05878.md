# [?] core/rawdb: fix data race between Retrieve and Close (#20919)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2020-04-14
Source: https://github.com/scroll-tech/go-ethereum/commit/2a836bb259c03626e5ef8435f99f341ea911bfff
Type: security-commit

## Details
core/rawdb: fix data race between Retrieve and Close (#20919)

* core/rawdb: fixed data race between retrieve and close

closes https://github.com/ethereum/go-ethereum/issues/20420

* core/rawdb: use non-atomic load while holding mutex

## Patch
### core/rawdb/freezer_table.go
```diff
@@ -541,20 +541,22 @@ func (t *freezerTable) getBounds(item uint64) (uint32, uint32, uint32, error) {
 // Retrieve looks up the data offset of an item with the given number and retrieves
 // the raw binary blob from the data file.
 func (t *freezerTable) Retrieve(item uint64) ([]byte, error) {
+	t.lock.RLock()
 	// Ensure the table and the item is accessible
 	if t.index == nil || t.head == nil {
+		t.lock.RUnlock()
 		return nil, errClosed
 	}
 	if atomic.LoadUint64(&t.items) <= item {
+		t.lock.RUnlock()
 		return nil, errOutOfBounds
 	}
 	// Ensure the item was not deleted from the tail either
-	offset := atomic.LoadUint32(&t.itemOffset)
-	if uint64(offset) > item {
+	if uint64(t.itemOffset) > item {
+		t.lock.RUnlock()
 		return nil, errOutOfBounds
 	}
-	t.lock.RLock()
-	startOffset, endOffset, filenum, err := t.getBounds(item - uint64(offset))
+	startOffset, endOffset, filenum, err := t.getBounds(item - uint64(t.itemOffset))
 	if err != nil {
 		t.lock.RUnlock()
 		return nil, err
```
