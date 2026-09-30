# [?] rpcserver: fix race condition in graph cache eviction

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-07-09
Source: https://github.com/lightningnetwork/lnd/commit/ef181adbc8bd4c41952a6a564e64bc842543ef90
Type: security-commit

## Details
rpcserver: fix race condition in graph cache eviction

The previous implementation of the graph cache evictor used
time.AfterFunc, which introduced a race condition. The closure
passed to AfterFunc could execute before the call returned and
assigned the timer to the r.graphCacheEvictor field.

This created a scenario where the closure would attempt to call
Reset() on a nil r.graphCacheEvictor, causing a panic.

This commit fixes the race by replacing time.AfterFunc with a
more robust pattern using time.NewTimer and a dedicated goroutine.
The new timer is created and assigned immediately, ensuring that
r.graphCacheEvictor is never nil when accessed.

The dedicated goroutine now safely manages the timer's lifecycle,
resetting it upon firing and stopping it gracefully upon server
shutdown, which also prevents goroutine leaks.

## Patch
### rpcserver.go
```diff
@@ -874,18 +874,39 @@ func (r *rpcServer) addDeps(ctx context.Context, s *server,
 
 	graphCacheDuration := r.cfg.Caches.RPCGraphCacheDuration
 	if graphCacheDuration != 0 {
-		r.graphCacheEvictor = time.AfterFunc(graphCacheDuration, func() {
-			// Grab the mutex and purge the current populated
-			// describe graph response.
-			r.graphCache.Lock()
-			defer r.graphCache.Unlock()
+		r.graphCacheEvictor = time.NewTimer(graphCacheDuration)
 
-			r.describeGraphResp = nil
+		go func() {
+			for {
+				select {
+				// The timer fired, so we'll purge the graph
+				// cache.
+				case <-r.graphCacheEvictor.C:
+					r.graphCache.Lock()
+					r.describeGraphResp = nil
+					r.graphCache.Unlock()
+
+					// Reset the timer so we'll fire
+					// again after the specified
+					// duration.
+					r.graphCacheEvictor.Reset(
+						graphCacheDuration,
+					)
 
-			// Reset ourselves as well at the end so we run again
-			// after the duration.
-			r.graphCacheEvictor.Reset(graphCacheDuration)
-		})
+				// The server is quitting, so we'll stop the
+				// timer and exit.
+				case <-r.quit:
+					if !r.graphCacheEvictor.Stop() {
+						// Drain the channel if Stop()
+						// returns false, meaning the
+						// timer has already fired.
+						<-r.graphCacheEvictor.C
+					}
+
+					return
+				}
+			}
+		}()
 	}
 
 	return nil
```
