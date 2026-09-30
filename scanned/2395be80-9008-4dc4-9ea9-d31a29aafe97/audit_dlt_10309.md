# [?] eth/downloader: fix a throughput estimation data race

## Summary
Severity: Unknown
Chain: Ronin
Component: axieinfinity/ronin-archive
Published: 2016-03-10
Source: https://github.com/axieinfinity/ronin-archive/commit/e3f2b541f2bd0433e997d0f8060934b181a5d0e0
Type: security-commit

## Details
eth/downloader: fix a throughput estimation data race

## Patch
### eth/downloader/peer.go
```diff
@@ -251,8 +251,8 @@ func (p *peer) setIdle(started time.Time, delivered int, throughput *float64, id
 	// Irrelevant of the scaling, make sure the peer ends up idle
 	defer atomic.StoreInt32(idle, 0)
 
-	p.lock.RLock()
-	defer p.lock.RUnlock()
+	p.lock.Lock()
+	defer p.lock.Unlock()
 
 	// If nothing was delivered (hard timeout / unavailable data), reduce throughput to minimum
 	if delivered == 0 {
```
