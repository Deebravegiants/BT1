# [?] swarm: Fix localstore test deadlock with race detector (#19153)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-02-22
Source: https://github.com/celo-org/celo-blockchain/commit/02c28046a04ebf649af5d1b2a702d0da1c8a2a39
Type: security-commit

## Details
swarm: Fix localstore test deadlock with race detector (#19153)

* swarm/storage/localstore: close localstore in two tests

* swarm/storage/localstore: fix a possible deadlock in tests

* swarm/storage/localstore: re-enable pull subs tests for travis race

* swarm/storage/localstore: stop sending to errChan on context done in tests

* swarm/storage/localstore: better want check in readPullSubscriptionBin

* swarm/storage/localstore: protect chunk put with addr lock in tests

* swamr/storage/localstore: wait for gc and writeGCSize workers on Close

* swarm/storage/localstore: more correct testDB_collectGarbageWorker

* swarm/storage/localstore: set DB Close timeout to 5s

## Patch
### swarm/storage/localstore/gc.go
```diff
@@ -117,6 +117,8 @@ var (
 // run. GC run iterates on gcIndex and removes older items
 // form retrieval and other indexes.
 func (db *DB) collectGarbageWorker() {
+	defer close(db.collectGarbageWorkerDone)
+
 	for {
 		select {
 		case <-db.collectGarbageTrigger:
@@ -132,7 +134,7 @@ func (db *DB) collectGarbageWorker() {
 				db.triggerGarbageCollection()
 			}
 
-			if testHookCollectGarbage != nil {
+			if collectedCount > 0 && testHookCollectGarbage != nil {
 				testHookCollectGarbage(collectedCount)
 			}
 		case <-db.close:
@@ -243,6 +245,8 @@ func (db *DB) triggerGarbageCollection() {
 // writeGCSizeDelay duration to avoid very frequent
 // database operations.
 func (db *DB) writeGCSizeWorker() {
+	defer close(db.writeGCSizeWorkerDone)
+
 	for {
 		select {
 		case <-db.writeGCSizeTrigger:
```

### swarm/storage/localstore/gc_test.go
```diff
@@ -118,15 +118,6 @@ func testDB_collectGarbageWorker(t *testing.T) {
 			t.Fatal(err)
 		}
 	})
-
-	// cleanup: drain the last testHookCollectGarbageChan
-	// element before calling deferred functions not to block
-	// collectGarbageWorker loop, preventing the race in
-	// setting testHookCollectGarbage function
-	select {
-	case <-testHookCollectGarbageChan:
-	default:
-	}
 }
 
 // TestDB_collectGarbageWorker_withRequests is a helper test function
@@ -290,6 +281,7 @@ func TestDB_gcSize(t *testing.T) {
 	if err != nil {
 		t.Fatal(err)
 	}
+	defer db.Close()
 
 	t.Run("gc index size", newIndexGCSizeTest(db))
 
```

### swarm/storage/localstore/localstore.go
```diff
@@ -107,6 +107,12 @@ type DB struct {
 	// this channel is closed when close function is called
 	// to terminate other goroutines
 	close chan struct{}
+
+	// protect Close method from exiting before
+	// garbage collection and gc size write workers
+	// are done
+	collectGarbageWorkerDone chan struct{}
+	writeGCSizeWorkerDone    chan struct{}
 }
 
 // Options struct holds optional parameters for configuring DB.
@@ -138,9 +144,11 @@ func New(path string, baseKey []byte, o *Options) (db *DB, err error) {
 		// need to be buffered with the size of 1
 		// to signal another event if it
 		// is triggered during already running function
-		collectGarbageTrigger: make(chan struct{}, 1),
-		writeGCSizeTrigger:    make(chan struct{}, 1),
-		close:                 make(chan struct{}),
+		collectGarbageTrigger:    make(chan struct{}, 1),
+		writeGCSizeTrigger:       make(chan struct{}, 1),
+		close:                    make(chan struct{}),
+		collectGarbageWorkerDone: make(chan struct{}),
+		writeGCSizeWorkerDone:    make(chan struct{}),
 	}
 	if db.capacity <= 0 {
 		db.capacity = defaultCapacity
@@ -361,6 +369,21 @@ func New(path string, baseKey []byte, o *Options) (db *DB, err error) {
 func (db *DB) Close() (err error) {
 	close(db.close)
 	db.updateGCWG.Wait()
+
+	// wait for gc worker and gc size write workers to
+	// return before closing the shed
+	timeout := time.After(5 * time.Second)
+	select {
+	case <-db.collectGarbageWorkerDone:
+	case <-timeout:
+		log.Error("localstore: collect garbage worker did not return after db close")
+	}
+	select {
+	case <-db.writeGCSizeWorkerDone:
+	case <-timeout:
+		log.Error("localstore: write gc size worker did not return after db close")
+	}
+
 	if err := db.writeGCSize(db.getGCSize()); err != nil {
 		log.Error("localstore: write gc size", "err", err)
 	}
```

### swarm/storage/localstore/localstore_test.go
```diff
@@ -163,6 +163,7 @@ func BenchmarkNew(b *testing.B) {
 			if err != nil {
 				b.Fatal(err)
 			}
+			defer db.Close()
 			uploader := db.NewPutter(ModePutUpload)
 			syncer := db.NewSetter(ModeSetSync)
 			for i := 0; i < count; i++ {
```

### swarm/storage/localstore/subscription_pull_test.go
```diff
@@ -20,26 +20,18 @@ import (
 	"bytes"
 	"context"
 	"fmt"
-	"os"
 	"sync"
 	"testing"
 	"time"
 
 	"github.com/ethereum/go-ethereum/swarm/storage"
-	"github.com/ethereum/go-ethereum/swarm/testutil"
 )
 
 // TestDB_SubscribePull uploads some chunks before and after
 // pull syncing subscription is created and validates if
 // all addresses are received in the right order
 // for expected proximity order bins.
 func TestDB_SubscribePull(t *testing.T) {
-
-	if testutil.RaceEnabled && os.Getenv("TRAVIS") == "true" {
-		t.Skip("does not complete with -race on Travis")
-		// Note: related ticket TODO
-	}
-
 	db, cleanupFunc := newTestDB(t, nil)
 	defer cleanupFunc()
 
@@ -87,12 +79,6 @@ func TestDB_SubscribePull(t *testing.T) {
 // validates if all addresses are received in the right order
 // for expected proximity order bins.
 func TestDB_SubscribePull_multiple(t *testing.T) {
-
-	if testutil.RaceEnabled && os.Getenv("TRAVIS") == "true" {
-		t.Skip("does not complete with -race on Travis")
-		// Note: related ticket TODO
-	}
-
 	db, cleanupFunc := newTestDB(t, nil)
 	defer cleanupFunc()
 
@@ -146,12 +132,6 @@ func TestDB_SubscribePull_multiple(t *testing.T) {
 // and validates if all expected addresses are received in the
 // right order for expected proximity order bins.
 func TestDB_SubscribePull_since(t *testing.T) {
-
-	if testutil.RaceEnabled && os.Getenv("TRAVIS") == "true" {
-		t.Skip("does not complete with -race on Travis")
-		// Note: related ticket TODO
-	}
-
 	db, cleanupFunc := newTestDB(t, nil)
 	defer cleanupFunc()
 
@@ -171,6 +151,9 @@ func TestDB_SubscribePull_since(t *testing.T) {
 	})()
 
 	uploadRandomChunks := func(count int, wanted bool) (last map[uint8]ChunkDescriptor) {
+		addrsMu.Lock()
+		defer addrsMu.Unlock()
+
 		last = make(map[uint8]ChunkDescriptor)
 		for i := 0; i < count; i++ {
 			chunk := generateRandomChunk()
@@ -182,15 +165,13 @@ func TestDB_SubscribePull_since(t *testing.T) {
 
 			bin := db.po(chunk.Address())
 
-			addrsMu.Lock()
 			if _, ok := addrs[bin]; !ok {
 				addrs[bin] = make([]storage.Address, 0)
 			}
 			if wanted {
 				addrs[bin] = append(addrs[bin], chunk.Address())
 				wantedChunksCount++
 			}
-			addrsMu.Unlock()
 
 			lastTimestampMu.RLock()
 			storeTimestamp := lastTimestamp
@@ -242,12 +223,6 @@ func TestDB_SubscribePull_since(t *testing.T) {
 // and validates if all expected addresses are received in the
 // right order for expected proximity order bins.
 func TestDB_SubscribePull_until(t *testing.T) {
-
-	if testutil.RaceEnabled && os.Getenv("TRAVIS") == "true" {
-		t.Skip("does not complete with -race on Travis")
-		// Note: related ticket TODO
-	}
-
 	db, cleanupFunc := newTestDB(t, nil)
 	defer cleanupFunc()
 
@@ -267,6 +242,9 @@ func TestDB_SubscribePull_until(t *testing.T) {
 	})()
 
 	uploadRandomChunks := func(count int, wanted bool) (last map[uint8]ChunkDescriptor) {
+		addrsMu.Lock()
+		defer addrsMu.Unlock()
+
 		last = make(map[uint8]ChunkDescriptor)
 		for i := 0; i < count; i++ {
 			chunk := generateRandomChunk()
@@ -278,15 +256,13 @@ func TestDB_SubscribePull_until(t *testing.T) {
 
 			bin := db.po(chunk.Address())
 
-			addrsMu.Lock()
 			if _, ok := addrs[bin]; !ok {
 				addrs[bin] = make([]storage.Address, 0)
 			}
 			if wanted {
 				addrs[bin] = append(addrs[bin], chunk.Address())
 				wantedChunksCount++
 			}
-			addrsMu.Unlock()
 
 			lastTimestampMu.RLock()
 			storeTimestamp := lastTimestamp
@@ -337,12 +313,6 @@ func TestDB_SubscribePull_until(t *testing.T) {
 // and until arguments, and validates if all expected addresses
 // are received in the right order for expected proximity order bins.
 func TestDB_SubscribePull_sinceAndUntil(t *testing.T) {
-
-	if testutil.RaceEnabled && os.Getenv("TRAVIS") == "true" {
-		t.Skip("does not complete with -race on Travis")
-		// Note: related ticket TODO
-	}
-
 	db, cleanupFunc := newTestDB(t, nil)
 	defer cleanupFunc()
 
@@ -362,6 +332,9 @@ func TestDB_SubscribePull_sinceAndUntil(t *testing.T) {
 	})()
 
 	uploadRandomChunks := func(count int, wanted bool) (last map[uint8]ChunkDescriptor) {
+		addrsMu.Lock()
+		defer addrsMu.Unlock()
+
 		last = make(map[uint8]ChunkDescriptor)
 		for i := 0; i < count; i++ {
 			chunk := generateRandomChunk()
@@ -373,15 +346,13 @@ func TestDB_SubscribePull_sinceAndUntil(t *testing.T) {
 
 			bin := db.po(chunk.Address())
 
-			addrsMu.Lock()
 			if _, ok := addrs[bin]; !ok {
 				addrs[bin] = make([]storage.Address, 0)
 			}
 			if wanted {
 				addrs[bin] = append(addrs[bin], chunk.Address())
 				wantedChunksCount++
 			}
-			addrsMu.Unlock()
 
 			lastTimestampMu.RLock()
 			storeTimestamp := lastTimestamp
@@ -442,6 +413,9 @@ func TestDB_SubscribePull_sinceAndUntil(t *testing.T) {
 // uploadRandomChunksBin uploads random chunks to database and adds them to
 // the map of addresses ber bin.
 func uploadRandomChunksBin(t *testing.T, db *DB, uploader *Putter, addrs map[uint8][]storage.Address, addrsMu *sync.Mutex, wantedChunksCount *int, count int) {
+	addrsMu.Lock()
+	defer addrsMu.Unlock()
+
 	for i := 0; i < count; i++ {
 		chunk := generateRandomChunk()
 
@@ -450,13 +424,11 @@ func uploadRandomChunksBin(t *testing.T, db *DB, uploader *Putter, addrs map[uin
 			t.Fatal(err)
 		}
 
-		addrsMu.Lock()
 		bin := db.po(chunk.Address())
 		if _, ok := addrs[bin]; !ok {
 			addrs[bin] = make([]storage.Address, 0)
 		}
 		addrs[bin] = append(addrs[bin], chunk.Address())
-		addrsMu.Unlock()
 
 		*wantedChunksCount++
 	}
@@ -473,19 +445,24 @@ func readPullSubscriptionBin(ctx context.Context, bin uint8, ch <-chan ChunkDesc
 			if !ok {
 				return
 			}
+			var err error
 			addrsMu.Lock()
 			if i+1 > len(addrs[bin]) {
-				errChan <- fmt.Errorf("got more chunk addresses %v, then expected %v, for bin %v", i+1, len(addrs[bin]), bin)
+				err = fmt.Errorf("got more chunk addresses %v, then expected %v, for bin %v", i+1, len(addrs[bin]), bin)
+			} else {
+				want := addrs[bin][i]
+				if !bytes.Equal(got.Address, want) {
+					err = fmt.Errorf("got chunk address %v in bin %v %s, want %s", i, bin, got.Address.Hex(), want)
+				}
 			}
-			want := addrs[bin][i]
 			addrsMu.Unlock()
-			var err error
-			if !bytes.Equal(got.Address, want) {
-				err = fmt.Errorf("got chunk address %v in bin %v %s, want %s", i, bin, got.Address.Hex(), want)
-			}
 			i++
 			// send one and only one error per received address
-			errChan <- err
+			select {
+			case errChan <- err:
+			case <-ctx.Done():
+				return
+			}
 		case <-ctx.Done():
 			return
 		}
```

### swarm/storage/localstore/subscription_push_test.go
```diff
@@ -40,6 +40,9 @@ func TestDB_SubscribePush(t *testing.T) {
 	var chunksMu sync.Mutex
 
 	uploadRandomChunks := func(count int) {
+		chunksMu.Lock()
+		defer chunksMu.Unlock()
+
 		for i := 0; i < count; i++ {
 			chunk := generateRandomChunk()
 
@@ -48,9 +51,7 @@ func TestDB_SubscribePush(t *testing.T) {
 				t.Fatal(err)
 			}
 
-			chunksMu.Lock()
 			chunks = append(chunks, chunk)
-			chunksMu.Unlock()
 		}
 	}
 
@@ -90,7 +91,11 @@ func TestDB_SubscribePush(t *testing.T) {
 				}
 				i++
 				// send one and only one error per received address
-				errChan <- err
+				select {
+				case errChan <- err:
+				case <-ctx.Done():
+					return
+				}
 			case <-ctx.Done():
 				return
 			}
@@ -123,6 +128,9 @@ func TestDB_SubscribePush_multiple(t *testing.T) {
 	var addrsMu sync.Mutex
 
 	uploadRandomChunks := func(count int) {
+		addrsMu.Lock()
+		defer addrsMu.Unlock()
+
 		for i := 0; i < count; i++ {
 			chunk := generateRandomChunk()
 
@@ -131,9 +139,7 @@ func TestDB_SubscribePush_multiple(t *testing.T) {
 				t.Fatal(err)
 			}
 
-			addrsMu.Lock()
 			addrs = append(addrs, chunk.Address())
-			addrsMu.Unlock()
 		}
 	}
 
@@ -175,7 +181,11 @@ func TestDB_SubscribePush_multiple(t *testing.T) {
 					}
 					i++
 					// send one and only one error per received address
-					errChan <- err
+					select {
+					case errChan <- err:
+					case <-ctx.Done():
+						return
+					}
 				case <-ctx.Done():
 					return
 				}
```
