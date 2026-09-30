# [?] txnprovider/txpool: fix deadlock (#16680)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-08-15
Source: https://github.com/erigontech/erigon/commit/019f5f4c5603a8389a09a95d52c21ebe2cd26c62
Type: security-commit

## Details
txnprovider/txpool: fix deadlock (#16680)

part of https://github.com/erigontech/erigon/issues/14413

- in commit a149cbf53fd674a354bc3b5f0e1e8a79eb38cb85 I added a goroutine
dump just before the test timeout is reached to help spot a deadlock
- the following [CI
run](https://github.com/erigontech/erigon/actions/runs/16985462951/job/48153373260)
failed and the goroutine dump was printed 5 secs before the test ctx was
cancelled (due to the timeout) - so it captured everything nicely (look
for `goroutine dump timer expired` in the logs)

we can see that:
- `p.best` has acquired `p.lock` but it is waiting on acquiring the
`poolDB.BeginRo` semaphore which has a limit of `runtime.GOMAXPROCS(-1)
* 16` (search for `(*TxPool).best` in the dump)
- there are 64 goroutines that have acquired a `poolDB.RoTx` (via
`poolDB.View`) but are waiting on acquiring `p.lock` which `p.best`
holds (31 goroutines waiting in `GetRlp` and 33 in `IsLocal` - search
for `(*TxPool).GetRlp` and `(*TxPool).IsLocal` in the dump)
- these all come from the goroutines that are spawned to handle
`announcements := <-p.newPendingTxns` devp2p propagations (for new txns)
- 64/16=4 which matches the 4 CPU count for a Windows GitHub hosted
runner
[here](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
- we've deadlocked 😢 

the comment in the code tries to explain this situation and the solution
to it

## Patch
### txnprovider/txpool/pool.go
```diff
@@ -779,12 +779,28 @@ func (p *TxPool) Started() bool {
 
 func (p *TxPool) best(ctx context.Context, n int, txns *TxnsRlp, onTopOf, availableGas, availableBlobGas uint64, yielded mapset.Set[[32]byte], availableRlpSpace int) (bool, int, error) {
 	p.lock.Lock()
-	defer p.lock.Unlock()
-
 	for last := p.lastSeenBlock.Load(); last < onTopOf; last = p.lastSeenBlock.Load() {
 		p.logger.Debug("[txpool] Waiting for block", "expecting", onTopOf, "lastSeen", last, "txRequested", n, "pending", p.pending.Len(), "baseFee", p.baseFee.Len(), "queued", p.queued.Len())
 		p.lastSeenCond.Wait()
 	}
+	// Important: poolDB.BeginRo has a RoTxsLimiter which is implemented using a weighted semaphore object. This means
+	// that we are dealing with 2 locks at a time. All other usages in the pool that use both p.lock and poolDB.BeginRo
+	// first acquire the RoTx and then acquire p.lock. However, here we do the opposite - we first acquire p.lock and
+	// then try to acquire a RoTx. This creates an opportunity for a deadlock if we've acquired p.lock but at the same
+	// time there has been a burst of goroutines (N=roTxsLimit) that have all acquired a RoTx and are now trying to
+	// acquire p.lock which we've acquired here (the goroutines processing announcements := <-p.newPendingTxns in p.Run
+	// are one example). One solution is to first acquire a RoTx here and then p.lock as everywhere else. However, this
+	// won't work well if we wait in the "Waiting for block" loop for a while since our RoTx will then see stale data.
+	// Instead, we can release p.lock once we're past "Waiting for block" -> try to acquire RoTx -> try to acquire
+	// p.lock again as everywhere else.
+	p.lock.Unlock()
+	tx, err := p.poolDB.BeginRo(ctx)
+	if err != nil {
+		return false, 0, err
+	}
+	defer tx.Rollback()
+	p.lock.Lock()
+	defer p.lock.Unlock()
 
 	best := p.pending.best
 
@@ -800,12 +816,6 @@ func (p *TxPool) best(ctx context.Context, n int, txns *TxnsRlp, onTopOf, availa
 		p.logger.Debug("[txpool] Processing best request", "last", onTopOf, "txRequested", n, "txAvailable", len(best.ms), "txProcessed", i, "txReturned", count)
 	}()
 
-	tx, err := p.poolDB.BeginRo(ctx)
-	if err != nil {
-		return false, 0, err
-	}
-
-	defer tx.Rollback()
 	for ; count < n && i < len(best.ms); i++ {
 		// if we wouldn't have enough gas for a standard transaction then quit out early
 		if availableGas < params.TxGas {
```
