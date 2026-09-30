# [?] Fix slice out of bounds error in validator db migration (#8510)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2021-02-24
Source: https://github.com/OffchainLabs/prysm/commit/6e831920bfa08a300d2786f7039314b03ebbd3ab
Type: security-commit

## Details
Fix slice out of bounds error in validator db migration (#8510)

* Fix slice out of bounds error in validator db migration #8509

* Add regression testing

* make it double just in case

* gofmt

## Patch
### validator/db/kv/migration_source_target_epochs_bucket.go
```diff
@@ -132,7 +132,7 @@ func batchPublicKeys(publicKeys [][]byte, batchSize int) [][][]byte {
 	}
 	batch := make([][][]byte, 0)
 	for i := 0; i < len(publicKeys); i += batchSize {
-		if i+batchSize == len(publicKeys)+1 {
+		if i+batchSize >= len(publicKeys)+1 {
 			batch = append(batch, publicKeys[i:])
 		} else {
 			batch = append(batch, publicKeys[i:i+batchSize])
```

### validator/db/kv/migration_source_target_epochs_bucket_test.go
```diff
@@ -14,7 +14,9 @@ import (
 
 func TestStore_migrateSourceTargetEpochsBucketUp(t *testing.T) {
 	numEpochs := uint64(100)
-	numKeys := 50
+	// numKeys should be more than batch size for testing.
+	// See: https://github.com/prysmaticlabs/prysm/issues/8509
+	numKeys := 2*publicKeyMigrationBatchSize + 1
 	pubKeys := make([][48]byte, numKeys)
 	for i := 0; i < numKeys; i++ {
 		var pk [48]byte
@@ -113,7 +115,9 @@ func TestStore_migrateSourceTargetEpochsBucketUp(t *testing.T) {
 }
 
 func TestStore_migrateSourceTargetEpochsBucketDown(t *testing.T) {
-	numKeys := 50
+	// numKeys should be more than batch size for testing.
+	// See: https://github.com/prysmaticlabs/prysm/issues/8509
+	numKeys := 2*publicKeyMigrationBatchSize + 1
 	pubKeys := make([][48]byte, numKeys)
 	for i := 0; i < numKeys; i++ {
 		var pk [48]byte
```
