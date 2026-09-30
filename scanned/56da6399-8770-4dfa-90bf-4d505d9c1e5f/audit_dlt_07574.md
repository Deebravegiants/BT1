# [?] core/rawdb: fix underflow in freezer inspect for empty ancients (#33203)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-11-25
Source: https://github.com/ethereum/go-ethereum/commit/2a4847a7d1462cdda375429b447e7162514721e0
Type: security-commit

## Details
core/rawdb: fix underflow in freezer inspect for empty ancients (#33203)

## Patch
### core/rawdb/ancient_utils.go
```diff
@@ -34,14 +34,10 @@ type freezerInfo struct {
 	name  string      // The identifier of freezer
 	head  uint64      // The number of last stored item in the freezer
 	tail  uint64      // The number of first stored item in the freezer
+	count uint64      // The number of stored items in the freezer
 	sizes []tableSize // The storage size per table
 }
 
-// count returns the number of stored items in the freezer.
-func (info *freezerInfo) count() uint64 {
-	return info.head - info.tail + 1
-}
-
 // size returns the storage size of the entire freezer.
 func (info *freezerInfo) size() common.StorageSize {
 	var total common.StorageSize
@@ -65,14 +61,24 @@ func inspect(name string, order map[string]freezerTableConfig, reader ethdb.Anci
 	if err != nil {
 		return freezerInfo{}, err
 	}
-	info.head = ancients - 1
+	if ancients > 0 {
+		info.head = ancients - 1
+	} else {
+		info.head = 0
+	}
 
 	// Retrieve the number of first stored item
 	tail, err := reader.Tail()
 	if err != nil {
 		return freezerInfo{}, err
 	}
 	info.tail = tail
+
+	if ancients == 0 {
+		info.count = 0
+	} else {
+		info.count = info.head - info.tail + 1
+	}
 	return info, nil
 }
 
```

### core/rawdb/database.go
```diff
@@ -644,7 +644,7 @@ func InspectDatabase(db ethdb.Database, keyPrefix, keyStart []byte) error {
 				fmt.Sprintf("Ancient store (%s)", strings.Title(ancient.name)),
 				strings.Title(table.name),
 				table.size.String(),
-				fmt.Sprintf("%d", ancient.count()),
+				fmt.Sprintf("%d", ancient.count),
 			})
 		}
 		total.Add(uint64(ancient.size()))
```
