# [?] Fix data race: roundChangeTimer (#1659)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-08-09
Source: https://github.com/celo-org/celo-blockchain/commit/f82aa14059c9b1f210077123df2700b4c912f6f4
Type: security-commit

## Details
Fix data race: roundChangeTimer (#1659)

### Description

Add Mu to deal with data race around roundChangeTimer.

### Other changes

None

### Tested

`go test -race ./e2e_test` doesn't return data races on roundChangeTimer.

CI

### Related issues

- Fixes #1587 

### Backwards compatibility

Yes

## Patch
### consensus/istanbul/core/core.go
```diff
@@ -117,7 +117,9 @@ type core struct {
 
 	futurePreprepareTimer         *time.Timer
 	resendRoundChangeMessageTimer *time.Timer
-	roundChangeTimer              *time.Timer
+
+	roundChangeTimer   *time.Timer
+	roundChangeTimerMu sync.RWMutex
 
 	validateFn func([]byte, []byte) (common.Address, error)
 
@@ -679,10 +681,12 @@ func (c *core) stopFuturePreprepareTimer() {
 }
 
 func (c *core) stopRoundChangeTimer() {
+	c.roundChangeTimerMu.Lock()
 	if c.roundChangeTimer != nil {
 		c.roundChangeTimer.Stop()
 		c.roundChangeTimer = nil
 	}
+	c.roundChangeTimerMu.Unlock()
 }
 
 func (c *core) stopResendRoundChangeTimer() {
@@ -720,9 +724,11 @@ func (c *core) resetRoundChangeTimer() {
 
 	view := &istanbul.View{Sequence: c.current.Sequence(), Round: c.current.DesiredRound()}
 	timeout := c.getRoundChangeTimeout()
+	c.roundChangeTimerMu.Lock()
 	c.roundChangeTimer = time.AfterFunc(timeout, func() {
 		c.sendEvent(timeoutAndMoveToNextRoundEvent{view})
 	})
+	c.roundChangeTimerMu.Unlock()
 
 	if c.current.DesiredRound().Cmp(common.Big1) > 0 {
 		logger := c.newLogger("func", "resetRoundChangeTimer")
```
