# [?] Prevent deadlock when shutting down mdbx flusher (#14261)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-03-26
Source: https://github.com/erigontech/erigon/commit/9e8ecf229f4958ed0ad05adad648a456609cae36
Type: security-commit

## Details
Prevent deadlock when shutting down mdbx flusher (#14261)

Co-authored-by: antonis19 <antonis19@users.noreply.github.com>

## Patch
### erigon-lib/kv/mdbx/kv_mdbx.go
```diff
@@ -61,53 +61,60 @@ func WithChaindataTables(defaultBuckets kv.TableCfg) kv.TableCfg {
 
 // handles background process of periodically flushing commits to disk
 type PeriodicFlusher struct {
-	env              *mdbx.Env // mdbx environment to flush to
-	opts             MdbxOpts
-	ticker           *time.Ticker  // set ticker
-	syncPeriod       time.Duration // how often to flush
-	quitFlushingChan chan struct{} // to signal end of flushing
-	closed           atomic.Bool
+	env        *mdbx.Env // mdbx environment to flush to
+	opts       MdbxOpts
+	ticker     *time.Ticker  // set ticker
+	syncPeriod time.Duration // how often to flush
+	closed     atomic.Bool
+	doneWg     sync.WaitGroup
 }
 
 func newPeriodicFlusher(env *mdbx.Env, opts MdbxOpts, syncPeriod time.Duration) *PeriodicFlusher {
 	return &PeriodicFlusher{
-		env:              env,
-		opts:             opts,
-		ticker:           time.NewTicker(syncPeriod),
-		syncPeriod:       syncPeriod,
-		quitFlushingChan: make(chan struct{}),
+		env:        env,
+		opts:       opts,
+		ticker:     time.NewTicker(syncPeriod),
+		syncPeriod: syncPeriod,
+		doneWg:     sync.WaitGroup{},
 	}
 }
 
-func (flusher *PeriodicFlusher) Close() {
+func (flusher *PeriodicFlusher) shutdown() {
+	// flusher.lock.Lock()
+	// defer flusher.lock.Unlock()
 	swapped := flusher.closed.CompareAndSwap(false, true)
 	if !swapped {
 		return
 	}
 	if flusher.ticker != nil {
 		flusher.ticker.Stop() // Stop the ticker
 	}
-	close(flusher.quitFlushingChan) //  close channel to signal quit
+}
+
+func (flusher *PeriodicFlusher) Close() {
+	flusher.shutdown()
+	flusher.doneWg.Wait()
 }
 
 func (flusher *PeriodicFlusher) FlushInBackground(ctx context.Context) {
-	for {
-		select {
-		case <-flusher.ticker.C:
-			if err := flusher.env.Sync(true, false); err != nil {
-				flusher.opts.log.Error("Error during periodic mdbx sync", "err", err, "dbName", flusher.opts.label)
-			}
-		case _, ok := <-flusher.quitFlushingChan:
-			if !ok {
+	flusher.doneWg.Add(1)
+	go func(ctx context.Context) {
+		defer flusher.doneWg.Done()
+		for !flusher.closed.Load() {
+			select {
+			case <-flusher.ticker.C:
+				if err := flusher.env.Sync(true, false); err != nil {
+					flusher.opts.log.Error("Error during periodic mdbx sync", "err", err, "dbName", flusher.opts.label)
+				}
+			case <-ctx.Done():
+				// here the flusher is not closed explicitly from outside,
+				// so we must close it from within
+				flusher.shutdown()
 				return
+			default:
 			}
-		case <-ctx.Done():
-			// here the flusher is not closed explicitly from outside,
-			// so we must close it from within
-			flusher.ticker.Stop()
-			return
 		}
-	}
+	}(ctx)
 }
 
 type MdbxOpts struct {
@@ -425,9 +432,8 @@ func (opts MdbxOpts) Open(ctx context.Context) (kv.RwDB, error) {
 
 	if opts.HasFlag(mdbx.SafeNoSync) && opts.syncPeriod != 0 {
 		db.periodicFlusher = newPeriodicFlusher(env, opts, opts.syncPeriod)
-		go func(ctx context.Context) { // start goroutine periodically flushing to disk
-			db.periodicFlusher.FlushInBackground(ctx) // start flushing in background
-		}(ctx)
+		db.periodicFlusher.FlushInBackground(ctx) // start flushing in background
+
 	}
 
 	customBuckets := opts.bucketsCfg(kv.TablesCfgByLabel(opts.label))
```
