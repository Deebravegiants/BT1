# [?] service/block: fix race condition in `TestExtendedHeaderBroadcast`

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2021-12-11
Source: https://github.com/celestiaorg/celestia-node/commit/ac39f48047dda4c7b0c6707593e450a0914b01ac
Type: security-commit

## Details
service/block: fix race condition in `TestExtendedHeaderBroadcast`

add locks for maps in `mockFetcher` structure

Issue #283

## Patch
### service/block/event_test.go
```diff
@@ -2,6 +2,7 @@ package block
 
 import (
 	"context"
+	"sync"
 	"testing"
 	"time"
 
@@ -106,9 +107,14 @@ func TestExtendedHeaderBroadcast(t *testing.T) {
 
 // mockFetcher mocks away the `Fetcher` interface.
 type mockFetcher struct {
-	suite          *header.TestSuite
-	valSets        map[int64]*core.ValidatorSet
-	commits        map[int64]*core.Commit
+	suite *header.TestSuite
+
+	valSetsLock sync.Mutex
+	valSets     map[int64]*core.ValidatorSet
+
+	commitsLock sync.Mutex
+	commits     map[int64]*core.Commit
+
 	mockNewBlockCh chan *RawBlock
 }
 
@@ -117,10 +123,16 @@ func (m *mockFetcher) GetBlock(ctx context.Context, height *int64) (*RawBlock, e
 }
 
 func (m *mockFetcher) Commit(ctx context.Context, height *int64) (*core.Commit, error) {
+	m.commitsLock.Lock()
+	defer m.commitsLock.Unlock()
+
 	return m.commits[*height], nil
 }
 
 func (m *mockFetcher) ValidatorSet(ctx context.Context, height *int64) (*core.ValidatorSet, error) {
+	m.valSetsLock.Lock()
+	defer m.valSetsLock.Unlock()
+
 	return m.valSets[*height], nil
 }
 
@@ -149,8 +161,13 @@ func (m *mockFetcher) generateBlocksWithValidHeaders(t *testing.T, num int) []*R
 
 		rawBlocks[i] = b
 		// store commit and valset at height
+		m.commitsLock.Lock()
 		m.commits[b.Height] = eh.Commit
+		m.commitsLock.Unlock()
+
+		m.valSetsLock.Lock()
 		m.valSets[b.Height] = eh.ValidatorSet
+		m.valSetsLock.Unlock()
 
 		m.mockNewBlockCh <- b
 		prevEH = eh
```
