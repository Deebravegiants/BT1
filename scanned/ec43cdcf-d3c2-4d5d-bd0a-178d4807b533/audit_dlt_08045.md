# [?] swarm: fix a data race on startTime (#18511)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-01-24
Source: https://github.com/celo-org/celo-blockchain/commit/b774d0a507017b2ba7a0d02f6aa23a0a83d1a768
Type: security-commit

## Details
swarm: fix a data race on startTime (#18511)

(cherry picked from commit fa34429a2695f57bc0a96cd78f25e86700d8ee44)

## Patch
### swarm/swarm.go
```diff
@@ -56,7 +56,6 @@ import (
 )
 
 var (
-	startTime          time.Time
 	updateGaugesPeriod = 5 * time.Second
 	startCounter       = metrics.NewRegisteredCounter("stack,start", nil)
 	stopCounter        = metrics.NewRegisteredCounter("stack,stop", nil)
@@ -80,6 +79,7 @@ type Swarm struct {
 	swap              *swap.Swap
 	stateStore        *state.DBStore
 	accountingMetrics *protocols.AccountingMetrics
+	startTime         time.Time
 
 	tracerClose io.Closer
 }
@@ -344,7 +344,7 @@ Start is called when the stack is started
 */
 // implements the node.Service interface
 func (self *Swarm) Start(srv *p2p.Server) error {
-	startTime = time.Now()
+	self.startTime = time.Now()
 
 	self.tracerClose = tracing.Closer
 
@@ -414,7 +414,7 @@ func (self *Swarm) periodicallyUpdateGauges() {
 }
 
 func (self *Swarm) updateGauges() {
-	uptimeGauge.Update(time.Since(startTime).Nanoseconds())
+	uptimeGauge.Update(time.Since(self.startTime).Nanoseconds())
 	requestsCacheGauge.Update(int64(self.netStore.RequestsCacheLen()))
 }
 
```
