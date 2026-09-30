# [?] fix potential deadlock in p2p stream GetHealthSummary

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2026-02-09
Source: https://github.com/harmony-one/harmony/commit/9fe4dda9843a7b2ed199fca9b8c74dd09ba90de6
Type: security-commit

## Details
fix potential deadlock in p2p stream GetHealthSummary

## Patch
### p2p/stream/types/progress_tracker.go
```diff
@@ -129,17 +129,21 @@ func (pt *ProgressTracker) GetProgressRate() float64 {
 
 // GetHealthSummary returns a simple health summary focused on reading progress
 func (pt *ProgressTracker) GetHealthSummary() map[string]interface{} {
+	now := time.Now()
+	isHealthy := pt.IsHealthy()
+	shouldTimeout := pt.ShouldTimeout()
+
 	pt.mu.RLock()
 	defer pt.mu.RUnlock()
 
-	now := time.Now()
+	timeSinceProgress := now.Sub(pt.lastProgressTime)
 	return map[string]interface{}{
 		"totalBytesRead":    pt.totalBytesRead,
 		"lastProgressTime":  pt.lastProgressTime,
-		"timeSinceProgress": now.Sub(pt.lastProgressTime).String(),
+		"timeSinceProgress": timeSinceProgress.String(),
 		"timeoutDuration":   pt.timeoutDuration.String(),
 		"resetThreshold":    pt.resetThreshold,
-		"isHealthy":         pt.IsHealthy(),
-		"shouldTimeout":     pt.ShouldTimeout(),
+		"isHealthy":         isHealthy,
+		"shouldTimeout":     shouldTimeout,
 	}
 }
```
