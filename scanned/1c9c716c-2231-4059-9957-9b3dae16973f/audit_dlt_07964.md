# [?] Avoid leveldb panic on db.Stats() (#1753)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2022-08-08
Source: https://github.com/ava-labs/avalanchego/commit/52d9e1de9aaa1e702ff8943ab8a76d85e94e6f50
Type: security-commit

## Details
Avoid leveldb panic on db.Stats() (#1753)

## Patch
### database/leveldb/db.go
```diff
@@ -80,6 +80,10 @@ type Database struct {
 	closeOnce sync.Once
 	// closeCh is closed when Close() is called.
 	closeCh chan struct{}
+	// closeWg is used to wait for all goroutines created by New() to exit.
+	// This avoids racy behavior when Close() is called at the same time as
+	// Stats(). See: https://github.com/syndtr/goleveldb/issues/418
+	closeWg sync.WaitGroup
 }
 
 type config struct {
@@ -236,13 +240,16 @@ func New(file string, configBytes []byte, log logging.Logger, namespace string,
 			return nil, err
 		}
 		wrappedDB.metrics = metrics
+		wrappedDB.closeWg.Add(1)
 		go func() {
 			t := time.NewTicker(parsedConfig.MetricUpdateFrequency)
-			defer t.Stop()
+			defer func() {
+				t.Stop()
+				wrappedDB.closeWg.Done()
+			}()
 
 			for {
-				err := wrappedDB.updateMetrics()
-				if !wrappedDB.closed.GetValue() && err != nil {
+				if err := wrappedDB.updateMetrics(); err != nil {
 					log.Warn("failed to update leveldb metrics",
 						zap.Error(err),
 					)
@@ -345,6 +352,7 @@ func (db *Database) Close() error {
 	db.closeOnce.Do(func() {
 		close(db.closeCh)
 	})
+	db.closeWg.Wait()
 	return updateError(db.DB.Close())
 }
 
```
