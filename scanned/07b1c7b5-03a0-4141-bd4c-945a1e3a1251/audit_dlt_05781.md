# [?] fix(lp2p): fix autopool deadlock (#5584)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-01-26
Source: https://github.com/cometbft/cometbft/commit/ab7b1c478ae847edce2679feefc35f1559b91daf
Type: security-commit

## Details
fix(lp2p): fix autopool deadlock (#5584)

Closes STACK-2143

---

#### PR checklist

- [x] Tests written/updated
- [ ] Changelog entry added in `.changelog` (we use
[unclog](https://github.com/informalsystems/unclog) to manage our
changelog)
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Fixes autopool shutdown sequencing to prevent deadlocks during pool
stop.
>
> - **autopool**: Rework `Pool.Stop()`—early return unlock on
already-stopped/empty; close `stoppedCh` and `inbound` before releasing
the lock to unblock readers; wait for workers and add final log
> - **workers**: On closed `inbound`, workers now exit without invoking
`Stop`, avoiding recursive shutdown
> - *tests*: Minor import reordering in `state/validation_test.go`
>
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
06715fe7ccf8ec3d0b0a5a9cdfbde5b9937c61b9. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### internal/autopool/pool.go
```diff
@@ -130,9 +130,9 @@ func (p *Pool[T]) Start() {
 // safe to call multiple times
 func (p *Pool[T]) Stop() {
 	p.mu.Lock()
-	defer p.mu.Unlock()
 
 	if p.stopped() || len(p.workers) == 0 {
+		p.mu.Unlock()
 		return
 	}
 
@@ -146,11 +146,16 @@ func (p *Pool[T]) Stop() {
 		p.removeWorker(id)
 	}
 
+	// close stop chan first (!)
+	close(p.stoppedCh)
+	close(p.inbound)
+
+	// unblock read operations
+	p.mu.Unlock()
+
 	p.logger.Info("Waiting for workers to finish")
 	p.workersWg.Wait()
-
-	close(p.inbound)
-	close(p.stoppedCh)
+	p.logger.Info("Stopped pool")
 }
 
 // Push adds a message directly to the pool FIFO queue.
@@ -211,9 +216,8 @@ func (w *worker[T]) run() {
 			// worker received a close signal
 			return
 		case msg, ok := <-w.pool.inbound:
-			// channel is closed for all workers, stop the whole pool
+			// channel is closed, pool is stopping - just exit
 			if !ok {
-				w.pool.Stop()
 				return
 			}
 
```

### state/validation_test.go
```diff
@@ -1,10 +1,11 @@
 package state_test
 
 import (
-	"github.com/cometbft/cometbft/types/errors"
 	"testing"
 	"time"
 
+	"github.com/cometbft/cometbft/types/errors"
+
 	"github.com/stretchr/testify/assert"
 	"github.com/stretchr/testify/mock"
 	"github.com/stretchr/testify/require"
```
