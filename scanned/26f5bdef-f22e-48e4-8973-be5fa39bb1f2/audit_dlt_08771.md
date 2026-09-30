# [?] eth/downloader: fix a data race in a log output

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2016-10-21
Source: https://github.com/scroll-tech/go-ethereum/commit/53db80da89ac736614cfcfc10ea40ac5f91b2646
Type: security-commit

## Details
eth/downloader: fix a data race in a log output

## Patch
### eth/downloader/downloader.go
```diff
@@ -948,11 +948,12 @@ func (d *Downloader) fetchNodeData() error {
 				}
 				d.syncStatsLock.Lock()
 				d.syncStatsStateDone += uint64(delivered)
+				syncStatsStateDone := d.syncStatsStateDone // Thread safe copy for the log below
 				d.syncStatsLock.Unlock()
 
 				// Log a message to the user and return
 				if delivered > 0 {
-					glog.V(logger.Info).Infof("imported %3d state entries in %9v: processed %d, pending at least %d", delivered, common.PrettyDuration(time.Since(start)), d.syncStatsStateDone, pending)
+					glog.V(logger.Info).Infof("imported %3d state entries in %9v: processed %d, pending at least %d", delivered, common.PrettyDuration(time.Since(start)), syncStatsStateDone, pending)
 				}
 			})
 		}
```
