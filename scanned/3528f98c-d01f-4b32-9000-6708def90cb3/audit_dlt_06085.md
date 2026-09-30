# [?] Fix data race in TxPool.Stop from duplicate shutdown calls (#1111)

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2026-08-05
Source: https://github.com/0xsoniclabs/sonic/commit/e95c9e9549f3ea7f5ac7abbdd8b374c403987e31
Type: security-commit

## Details
Fix data race in TxPool.Stop from duplicate shutdown calls (#1111)

* Fix data race in TxPool.Stop from duplicate shutdown calls

TxPool.Stop() could be invoked concurrently: once via gossip.Service's
node lifecycle shutdown, and once via config.MakeNode's cleanup chain.
Both paths raced on the unguarded txJournal.writer field. Guard Stop()
with sync.Once so it's safe to call more than once.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

* Use structured log

---------

Co-authored-by: Claude Sonnet 5 <noreply@anthropic.com>

## Patch
### evmcore/tx_pool.go
```diff
@@ -330,6 +330,7 @@ type TxPool struct {
 	reorgDoneCh     chan chan struct{}
 	reorgShutdownCh chan struct{}  // requests shutdown of scheduleReorgLoop
 	wg              sync.WaitGroup // tracks loop, scheduleReorgLoop
+	stopOnce        sync.Once      // ensures Stop is only executed once, even if invoked concurrently
 
 	waitForIdleReorgLoopRequestCh  chan struct{} // requests to wait for reorg completion
 	waitForIdleReorgLoopResponseCh chan struct{} // responses to waitForReorgDoneRequestCh
@@ -506,21 +507,25 @@ func (pool *TxPool) loop() {
 	}
 }
 
-// Stop terminates the transaction pool.
+// Stop terminates the transaction pool. It is called both by the gossip
+// service's own shutdown and by config.MakeNode's cleanup chain, so it must
+// tolerate being invoked more than once, including concurrently.
 func (pool *TxPool) Stop() {
-	// Unsubscribe all subscriptions registered from txpool
-	pool.scope.Close()
+	pool.stopOnce.Do(func() {
+		// Unsubscribe all subscriptions registered from txpool
+		pool.scope.Close()
 
-	// Unsubscribe subscriptions registered from blockchain
-	pool.chainHeadSub.Unsubscribe()
-	pool.wg.Wait()
+		// Unsubscribe subscriptions registered from blockchain
+		pool.chainHeadSub.Unsubscribe()
+		pool.wg.Wait()
 
-	if pool.journal != nil {
-		if err := pool.journal.close(); err != nil {
-			log.Warn("Failed to close transaction journal:", err)
+		if pool.journal != nil {
+			if err := pool.journal.close(); err != nil {
+				log.Warn("Failed to close transaction journal:", "err", err)
+			}
 		}
-	}
-	log.Info("Transaction pool stopped")
+		log.Info("Transaction pool stopped")
+	})
 }
 
 // SubscribeNewTxsNotify registers a subscription of NewTxsNotify and
```
