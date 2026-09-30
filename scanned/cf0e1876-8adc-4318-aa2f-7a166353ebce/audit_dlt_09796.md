# [?] Fix deadlock in Downloader loop and improve handling of downloadC signals #4865

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2025-03-06
Source: https://github.com/harmony-one/harmony/commit/a90922918cb4a6d6aa8bb9138a7809040f689ce9
Type: security-commit

## Details
Fix deadlock in Downloader loop and improve handling of downloadC signals #4865

## Patch
### api/service/stagedstreamsync/downloader.go
```diff
@@ -251,11 +251,7 @@ func (d *Downloader) loop() {
 			trigger()
 
 		case <-d.downloadC:
-			go func() {
-				d.syncMutex.Lock()
-				defer d.syncMutex.Unlock()
-				d.handleDownload(&initSync, trigger)
-			}()
+			go d.handleDownload(&initSync, trigger)
 
 		case <-d.closeC:
 			return
```

### p2p/stream/protocols/sync/protocol.go
```diff
@@ -243,11 +243,11 @@ func (p *Protocol) advertise() time.Duration {
 	maxRetries := 3
 
 	// Constants for timeout adjustments
-	baseTimeout := 60 * time.Second          // Initial timeout for the advertise call
-	timeoutIncrementStep := 10 * time.Second // Increase timeout if context deadline is exceeded
-	maxTimeout := 5 * time.Minute            // Maximum allowed timeout
-	backoffTimeRatio := 2 * time.Second      // Base time for exponential backoff
-	maxBackoff := 10 * time.Second           // Cap for the exponential backoff delay
+	baseTimeout := 300 * time.Second         // Initial timeout for the advertise call
+	timeoutIncrementStep := 30 * time.Second // Increase timeout if context deadline is exceeded
+	maxTimeout := 600 * time.Second          // Maximum allowed timeout
+	backoffTimeRatio := 5 * time.Second      // Base time for exponential backoff
+	maxBackoff := 30 * time.Second           // Cap for the exponential backoff delay
 
 	timeout := baseTimeout
 
@@ -275,7 +275,7 @@ func (p *Protocol) advertise() time.Duration {
 				newPeersDiscovered = true
 				p.logger.Info().
 					Str("protocol", string(pid)).
-					Dur("elapsed", elapsed).
+					Dur("elapsed(sec)", time.Duration(elapsed.Seconds())).
 					Int("retry", retries).
 					Msg("Advertise call completed")
 				break
@@ -284,12 +284,14 @@ func (p *Protocol) advertise() time.Duration {
 			p.logger.Debug().Err(err).
 				Str("protocol", string(pid)).
 				Int("retry", retries).
+				Dur("elapsed(sec)", time.Duration(elapsed.Seconds())).
 				Msg("Advertise failed, retrying")
 
 			// If the error is a timeout, increase the timeout duration
 			if errors.Is(err, context.DeadlineExceeded) {
 				p.logger.Debug().
 					Str("protocol", string(pid)).
+					Dur("elapsed(sec)", time.Duration(elapsed.Seconds())).
 					Msg("Advertise failed due to timeout, increasing timeout")
 
 				timeout += timeoutIncrementStep
```
