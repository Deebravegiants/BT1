# [?] swarm/storage/localstore: fix testDB_collectGarbageWorker data race (#19206)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-03-04
Source: https://github.com/celo-org/celo-blockchain/commit/216bd2ceba2eb1708b7bdc7d69cf2984ff972cbf
Type: security-commit

## Details
swarm/storage/localstore: fix testDB_collectGarbageWorker data race (#19206)

## Patch
### swarm/storage/localstore/gc_test.go
```diff
@@ -51,14 +51,16 @@ func testDB_collectGarbageWorker(t *testing.T) {
 
 	chunkCount := 150
 
-	testHookCollectGarbageChan := make(chan int64)
-	defer setTestHookCollectGarbage(func(collectedCount int64) {
-		testHookCollectGarbageChan <- collectedCount
-	})()
-
 	db, cleanupFunc := newTestDB(t, &Options{
 		Capacity: 100,
 	})
+	testHookCollectGarbageChan := make(chan int64)
+	defer setTestHookCollectGarbage(func(collectedCount int64) {
+		select {
+		case testHookCollectGarbageChan <- collectedCount:
+		case <-db.close:
+		}
+	})()
 	defer cleanupFunc()
 
 	uploader := db.NewPutter(ModePutUpload)
```
