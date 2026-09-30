# [?] node/cn: fix nil deref race in sidecarReqManager.update

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2026-04-13
Source: https://github.com/kaiachain/kaia/commit/534db158852c93e0482350a91bb06d41171ae097
Type: security-commit

## Details
node/cn: fix nil deref race in sidecarReqManager.update

Add a nil guard at the top of update() so that a concurrent delete()
(e.g. handleBlobSidecarsMsg removing the entry just before the sync
loop calls update()) results in a safe no-op instead of a panic.

Also add TestSidecarReqManager_UpdateNilEntry to cover the race path.

## Patch
### node/cn/handler.go
```diff
@@ -1905,6 +1905,9 @@ func (m *sidecarReqManager) get(txHash common.Hash) *sidecarReq {
 func (m *sidecarReqManager) update(txHash common.Hash, peer string) {
 	m.mu.Lock()
 	defer m.mu.Unlock()
+	if m.list[txHash] == nil {
+		return // already deleted by a concurrent response
+	}
 	// no longer keep the request if the try count is too high
 	if m.list[txHash].try+1 >= m.maxTry {
 		delete(m.list, txHash)
```

### node/cn/handler_test.go
```diff
@@ -1574,6 +1574,28 @@ func TestSidecarReqManager_Update(t *testing.T) {
 	assert.Nil(t, req, "Request should be deleted when try >= maxTry")
 }
 
+// TestSidecarReqManager_UpdateNilEntry tests that update does not panic when the entry
+// has been concurrently deleted before update() acquires the lock.
+func TestSidecarReqManager_UpdateNilEntry(t *testing.T) {
+	m := newTestSidecarReqManager(10*time.Second, 5)
+	txHash := tx1.Hash()
+
+	// update on a never-added (nil) entry must not panic
+	assert.NotPanics(t, func() {
+		m.update(txHash, "peer-1")
+	}, "update on missing entry should be a no-op, not a panic")
+
+	// add, delete, then update — simulates the race: response arrives before update()
+	m.add(txHash, newTestBlobSidecarsRequestData(txHash, 100, 0))
+	m.delete(txHash)
+	assert.NotPanics(t, func() {
+		m.update(txHash, "peer-1")
+	}, "update after concurrent delete should be a no-op, not a panic")
+
+	// entry must remain absent
+	assert.Nil(t, m.get(txHash), "entry should remain deleted after no-op update")
+}
+
 // TestSidecarReqManager_Delete tests the delete method
 func TestSidecarReqManager_Delete(t *testing.T) {
 	cooldown := 10 * time.Second
```
