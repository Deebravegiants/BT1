# [?] [GOAL2-877] Fix data race in asyncVoteVerifier during shutdown (#171)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2019-07-19
Source: https://github.com/algorand/go-algorand/commit/a051ff41dc17d83f074ee7b6bfc8c93a4b85fcf4
Type: security-commit

## Details
[GOAL2-877] Fix data race in asyncVoteVerifier during shutdown (#171)

* Fix bug.

* unwrap anonymous function.

* add in-code comments.

## Patch
### agreement/asyncVoteVerifier.go
```diff
@@ -51,6 +51,7 @@ type asyncVerifyVoteResponse struct {
 type AsyncVoteVerifier struct {
 	done            chan struct{}
 	wg              sync.WaitGroup
+	workerWaitCh    chan struct{}
 	backlogExecPool execpool.BacklogPool
 	execpoolOut     chan interface{}
 	ctx             context.Context
@@ -76,19 +77,19 @@ func MakeAsyncVoteVerifier(verificationPool execpool.BacklogPool) *AsyncVoteVeri
 
 	verifier.ctx, verifier.ctxCancel = context.WithCancel(context.Background())
 
-	verifier.wg.Add(1)
+	verifier.workerWaitCh = make(chan struct{})
 	go verifier.worker()
 	return verifier
 }
 
 func (avv *AsyncVoteVerifier) worker() {
-	defer avv.wg.Done()
+	defer close(avv.workerWaitCh)
 	for res := range avv.execpoolOut {
 		asyncResponse := res.(*asyncVerifyVoteResponse)
-		if asyncResponse == nil {
-			continue
+		if asyncResponse != nil {
+			asyncResponse.req.out <- *asyncResponse
 		}
-		asyncResponse.req.out <- *asyncResponse
+		avv.wg.Done()
 	}
 }
 
@@ -129,7 +130,13 @@ func (avv *AsyncVoteVerifier) verifyVote(verctx context.Context, l LedgerReader,
 	default:
 		// if we're done while waiting for room in the requests channel, don't queue the request
 		req := asyncVerifyVoteRequest{ctx: verctx, l: l, uv: &uv, index: index, message: message, out: out}
-		avv.backlogExecPool.EnqueueBacklog(avv.ctx, avv.executeVoteVerification, req, avv.execpoolOut)
+		avv.wg.Add(1)
+		if avv.backlogExecPool.EnqueueBacklog(avv.ctx, avv.executeVoteVerification, req, avv.execpoolOut) != nil {
+			// we want to call "wg.Done()" here to "fix" the accounting of the number of pending tasks.
+			// if we got a non-nil, it means that our context has expired, which means that we won't see this task
+			// getting to the verification function.
+			avv.wg.Done()
+		}
 	}
 }
 
@@ -141,20 +148,31 @@ func (avv *AsyncVoteVerifier) verifyEqVote(verctx context.Context, l LedgerReade
 	default:
 		// if we're done while waiting for room in the requests channel, don't queue the request
 		req := asyncVerifyVoteRequest{ctx: verctx, l: l, uev: &uev, index: index, message: message, out: out}
-		avv.backlogExecPool.EnqueueBacklog(avv.ctx, avv.executeEqVoteVerification, req, avv.execpoolOut)
+		avv.wg.Add(1)
+		if avv.backlogExecPool.EnqueueBacklog(avv.ctx, avv.executeEqVoteVerification, req, avv.execpoolOut) != nil {
+			// we want to call "wg.Done()" here to "fix" the accounting of the number of pending tasks.
+			// if we got a non-nil, it means that our context has expired, which means that we won't see this task
+			// getting to the verification function.
+			avv.wg.Done()
+		}
 	}
 }
 
 // Quit tells the AsyncVoteVerifier to shutdown and waits until all workers terminate.
 func (avv *AsyncVoteVerifier) Quit() {
 	// indicate we're done and wait for all workers to finish
 	avv.ctxCancel()
+
+	// wait until all the tasks we've given the pool are done.
+	avv.wg.Wait()
 	if avv.backlogExecPool.GetOwner() == avv {
 		avv.backlogExecPool.Shutdown()
 	}
-	close(avv.execpoolOut)
-	avv.wg.Wait()
 
+	// since no more tasks are coming, we can safely close the output pool channel.
+	close(avv.execpoolOut)
+	// wait until the worker function exists.
+	<-avv.workerWaitCh
 }
 
 // Parallelism gives the maximum parallelism of the vote verifier.
```
