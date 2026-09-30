# [?] QBFT: prevent maximum request timeout overflow (#1665)

## Summary
Severity: Unknown
Chain: Quorum
Component: Consensys-inc-archive/quorum
Published: 2023-08-21
Source: https://github.com/Consensys-inc-archive/quorum/commit/c46b44c583aa7bad424b775d1c6f2325953cd862
Type: security-commit

## Details
QBFT: prevent maximum request timeout overflow (#1665)

## Patch
### consensus/istanbul/qbft/core/core.go
```diff
@@ -261,13 +261,32 @@ func (c *core) newRoundChangeTimer() {
 	// set timeout based on the round number
 	baseTimeout := time.Duration(c.config.GetConfig(c.current.Sequence()).RequestTimeout) * time.Millisecond
 	round := c.current.Round().Uint64()
-
-	timeout := baseTimeout * time.Duration(math.Pow(2, float64(round)))
-
 	maxRequestTimeout := time.Duration(c.config.GetConfig(c.current.Sequence()).MaxRequestTimeoutSeconds) * time.Second
 
-	if maxRequestTimeout > time.Duration(0) && timeout > maxRequestTimeout {
-		timeout = maxRequestTimeout
+	// If the upper limit of the request timeout is capped by small maxRequestTimeout, round can be a quite large number,
+	// which leads to float64 overflow, making its value negative or zero forever after some point.
+	// In this case we cannot simply use math.Pow and have to implement a safeguard on our own, at the cost of performance (which is not important in this case).
+	var timeout time.Duration
+	if maxRequestTimeout > time.Duration(0) {
+		timeout = baseTimeout
+		for i := uint64(0); i < round; i++ {
+			timeout = timeout * 2
+			if timeout > maxRequestTimeout {
+				timeout = maxRequestTimeout
+				break
+			}
+		}
+		// prevent log storm when unexpected overflow happens
+		if timeout < baseTimeout {
+			c.currentLogger(true, nil).Error("QBFT: Possible request timeout overflow detected, setting timeout value to maxRequestTimeout",
+				"timeout", timeout.Seconds(),
+				"max_request_timeout", maxRequestTimeout.Seconds(),
+			)
+			timeout = maxRequestTimeout
+		}
+	} else {
+		// effectively impossible to observe overflow happen when maxRequestTimeout is disabled
+		timeout = baseTimeout * time.Duration(math.Pow(2, float64(round)))
 	}
 
 	c.currentLogger(true, nil).Trace("QBFT: start new ROUND-CHANGE timer", "timeout", timeout.Seconds())
```
