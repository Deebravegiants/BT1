# [?] fix race condition in asyncflushproducer.OpenDB when the same DB is created twice

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2022-07-26
Source: https://github.com/0xsoniclabs/sonic/commit/bbcd5e31830f6153c5fd05e4c13e0723b718619b
Type: security-commit

## Details
fix race condition in asyncflushproducer.OpenDB when the same DB is created twice

## Patch
### utils/dbutil/asyncflushproducer/producer.go
```diff
@@ -27,10 +27,10 @@ func Wrap(backend kvdb.FullDBProducer, threshold uint64) *Producer {
 }
 
 func (f *Producer) OpenDB(name string) (kvdb.Store, error) {
-	// open existing DB
 	f.mu.Lock()
+	defer f.mu.Unlock()
+	// open existing DB
 	openedDB := f.dbs[name]
-	f.mu.Unlock()
 	if openedDB != nil {
 		return openedDB, nil
 	}
@@ -39,8 +39,6 @@ func (f *Producer) OpenDB(name string) (kvdb.Store, error) {
 	if err != nil {
 		return nil, err
 	}
-	f.mu.Lock()
-	defer f.mu.Unlock()
 	if f.dbs[name] != nil {
 		return nil, errors.New("already opened")
 	}
```
