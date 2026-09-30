# [?] triedb/pathdb: fix an deadlock in history indexer (#32260)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-07-23
Source: https://github.com/ethereum/go-ethereum/commit/16117eb7cddc4584865af106d2332aa89f387d3d
Type: security-commit

## Details
triedb/pathdb: fix an deadlock in history indexer (#32260)

Seems the `signal.result` was not sent back in shorten case, this will
cause a deadlock.

---------

Signed-off-by: jsvisa <delweng@gmail.com>
Co-authored-by: Gary Rong <garyrong0905@gmail.com>

## Patch
### triedb/pathdb/history_indexer.go
```diff
@@ -392,16 +392,17 @@ func (i *indexIniter) run(lastID uint64) {
 		select {
 		case signal := <-i.interrupt:
 			// The indexing limit can only be extended or shortened continuously.
-			if signal.newLastID != lastID+1 && signal.newLastID != lastID-1 {
-				signal.result <- fmt.Errorf("invalid history id, last: %d, got: %d", lastID, signal.newLastID)
+			newLastID := signal.newLastID
+			if newLastID != lastID+1 && newLastID != lastID-1 {
+				signal.result <- fmt.Errorf("invalid history id, last: %d, got: %d", lastID, newLastID)
 				continue
 			}
-			i.last.Store(signal.newLastID) // update indexing range
+			i.last.Store(newLastID) // update indexing range
 
 			// The index limit is extended by one, update the limit without
 			// interrupting the current background process.
-			if signal.newLastID == lastID+1 {
-				lastID = signal.newLastID
+			if newLastID == lastID+1 {
+				lastID = newLastID
 				signal.result <- nil
 				log.Debug("Extended state history range", "last", lastID)
 				continue
@@ -425,7 +426,9 @@ func (i *indexIniter) run(lastID uint64) {
 				return
 			}
 			// Adjust the indexing target and relaunch the process
-			lastID = signal.newLastID
+			lastID = newLastID
+			signal.result <- nil
+
 			done, interrupt = make(chan struct{}), new(atomic.Int32)
 			go i.index(done, interrupt, lastID)
 			log.Debug("Shortened state history range", "last", lastID)
```

### triedb/pathdb/history_indexer_test.go
```diff
@@ -0,0 +1,57 @@
+// Copyright 2025 The go-ethereum Authors
+// This file is part of the go-ethereum library.
+//
+// The go-ethereum library is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// The go-ethereum library is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with the go-ethereum library. If not, see <http://www.gnu.org/licenses/>.
+
+package pathdb
+
+import (
+	"testing"
+	"time"
+
+	"github.com/ethereum/go-ethereum/core/rawdb"
+)
+
+// TestHistoryIndexerShortenDeadlock tests that a call to shorten does not
+// deadlock when the indexer is active. This specifically targets the case where
+// signal.result must be sent to unblock the caller.
+func TestHistoryIndexerShortenDeadlock(t *testing.T) {
+	//log.SetDefault(log.NewLogger(log.NewTerminalHandlerWithLevel(os.Stderr, log.LevelInfo, true)))
+	db := rawdb.NewMemoryDatabase()
+	freezer, _ := rawdb.NewStateFreezer(t.TempDir(), false, false)
+	defer freezer.Close()
+
+	histories := makeHistories(100)
+	for i, h := range histories {
+		accountData, storageData, accountIndex, storageIndex := h.encode()
+		rawdb.WriteStateHistory(freezer, uint64(i+1), h.meta.encode(), accountIndex, storageIndex, accountData, storageData)
+	}
+	// As a workaround, assign a future block to keep the initer running indefinitely
+	indexer := newHistoryIndexer(db, freezer, 200)
+	defer indexer.close()
+
+	done := make(chan error, 1)
+	go func() {
+		done <- indexer.shorten(200)
+	}()
+
+	select {
+	case err := <-done:
+		if err != nil {
+			t.Fatalf("shorten returned an unexpected error: %v", err)
+		}
+	case <-time.After(2 * time.Second):
+		t.Fatal("timed out waiting for shorten to complete, potential deadlock")
+	}
+}
```
