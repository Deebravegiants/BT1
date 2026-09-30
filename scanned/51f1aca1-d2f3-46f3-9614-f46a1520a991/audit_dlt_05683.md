# [?] Fix resendRoundChangeMessageTimer data race

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-09-22
Source: https://github.com/celo-org/celo-blockchain/commit/0722c7d7fa5aca080f8b77912529a01988d26d3e
Type: security-commit

## Details
Fix resendRoundChangeMessageTimer data race

core.resetResendRoundChangeTimer was being called from the main engine
go-routine and core.stopResendRoundChangeTimer was being called via
core.Stop from miner's update go-routine. Both accessed
resendRoundChangeMessageTimer without syncronisation.

This commit adds a mutex to ensure synchronised access to
resendRoundChangeMessageTimer.

==================
WARNING: DATA RACE
Read at 0x00c01377f568 by goroutine 72:
  github.com/celo-org/celo-blockchain/consensus/istanbul/core.(*core).stopResendRoundChangeTimer()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/core/core.go:710 +0x47
  github.com/celo-org/celo-blockchain/consensus/istanbul/core.(*core).stopAllTimers()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/core/core.go:719 +0x54
  github.com/celo-org/celo-blockchain/consensus/istanbul/core.(*core).Stop()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/core/handler.go:61 +0x44
  github.com/celo-org/celo-blockchain/consensus/istanbul/backend.(*Backend).StopValidating()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/backend/engine.go:707 +0x193
  github.com/celo-org/celo-blockchain/miner.(*worker).stop()
      /home/pierspowlesland/projects/celo-blockchain/miner/worker.go:220 +0xbb
  github.com/celo-org/celo-blockchain/miner.(*Miner).update()
      /home/pierspowlesland/projects/celo-blockchain/miner/miner.go:173 +0x6fb

Previous write at 0x00c01377f568 by goroutine 312:
  github.com/celo-org/celo-blockchain/consensus/istanbul/core.(*core).resetResendRoundChangeTimer()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/core/core.go:780 +0x368
  github.com/celo-org/celo-blockchain/consensus/istanbul/core.(*core).resendRoundChangeMessage()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/core/core.go:795 +0x7b
  github.com/celo-org/celo-blockchain/consensus/istanbul/core.(*core).handleResendRoundChangeEvent()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/core/handler.go:247 +0x353
  github.com/celo-org/celo-blockchain/consensus/istanbul/core.(*core).handleEvents()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/core/handler.go:143 +0x77e

## Patch
### consensus/istanbul/core/core.go
```diff
@@ -115,8 +115,9 @@ type core struct {
 	finalCommittedSub *event.TypeMuxSubscription
 	timeoutSub        *event.TypeMuxSubscription
 
-	futurePreprepareTimer         *time.Timer
-	resendRoundChangeMessageTimer *time.Timer
+	futurePreprepareTimer           *time.Timer
+	resendRoundChangeMessageTimer   *time.Timer
+	resendRoundChangeMessageTimerMu sync.Mutex
 
 	roundChangeTimer   *time.Timer
 	roundChangeTimerMu sync.RWMutex
@@ -688,6 +689,8 @@ func (c *core) stopRoundChangeTimer() {
 }
 
 func (c *core) stopResendRoundChangeTimer() {
+	c.resendRoundChangeMessageTimerMu.Lock()
+	defer c.resendRoundChangeMessageTimerMu.Unlock()
 	if c.resendRoundChangeMessageTimer != nil {
 		c.resendRoundChangeMessageTimer.Stop()
 		c.resendRoundChangeMessageTimer = nil
@@ -777,6 +780,8 @@ func (c *core) resetResendRoundChangeTimer() {
 			resendTimeout = maxResendTimeout
 		}
 		view := &istanbul.View{Sequence: c.current.Sequence(), Round: c.current.DesiredRound()}
+		c.resendRoundChangeMessageTimerMu.Lock()
+		defer c.resendRoundChangeMessageTimerMu.Unlock()
 		c.resendRoundChangeMessageTimer = time.AfterFunc(resendTimeout, func() {
 			c.sendEvent(resendRoundChangeEvent{view})
 		})
```
