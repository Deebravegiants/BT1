# [?] fix(rpc): Race condition when waiting for response on `broadcast_tx_sync/commit` (#3193)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-06-05
Source: https://github.com/cometbft/cometbft/commit/cd465c51f9253a579d01298ce698806bf2283bd9
Type: security-commit

## Details
fix(rpc): Race condition when waiting for response on `broadcast_tx_sync/commit` (#3193)

This PR fixes a race condition generated when calling
`broadcast_tx_sync` and `broadcast_tx_commit`. When closing the context,
we want to also close the goroutine waiting for the response with
`reqRes.Wait()`. We don't need to do `reqRes.Done()` because there is a
chance it may become negative; instead, we just let the ABCI client to
do it.

This bug was recently introduced by #3131.


---

#### PR checklist

- [ ] Tests written/updated
- [ ] Changelog entry added in `.changelog` (we use
[unclog](https://github.com/informalsystems/unclog) to manage our
changelog)
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments
- [ ] Title follows the [Conventional
Commits](https://www.conventionalcommits.org/en/v1.0.0/) spec

## Patch
### rpc/core/mempool.go
```diff
@@ -47,7 +47,9 @@ func (env *Environment) BroadcastTxSync(ctx *rpctypes.Context, tx types.Tx) (*ct
 		return nil, err
 	}
 	go func() {
-		reqRes.Wait() // wait for response
+		// Wait for a response. The ABCI client guarantees that it will eventually call
+		// reqRes.Done(), even in the case of error.
+		reqRes.Wait()
 		select {
 		case <-ctx.Context().Done():
 		default:
@@ -58,7 +60,6 @@ func (env *Environment) BroadcastTxSync(ctx *rpctypes.Context, tx types.Tx) (*ct
 
 	select {
 	case <-ctx.Context().Done():
-		reqRes.Done() // release waiter on goroutine
 		return nil, ErrTxBroadcast{Source: ctx.Context().Err(), ErrReason: ErrConfirmationNotReceived}
 	case res := <-resCh:
 		return &ctypes.ResultBroadcastTx{
@@ -110,7 +111,9 @@ func (env *Environment) BroadcastTxCommit(ctx *rpctypes.Context, tx types.Tx) (*
 		return nil, ErrTxBroadcast{Source: err, ErrReason: ErrCheckTxFailed}
 	}
 	go func() {
-		reqRes.Wait() // wait for response
+		// Wait for a response. The ABCI client guarantees that it will eventually call
+		// reqRes.Done(), even in the case of error.
+		reqRes.Wait()
 		select {
 		case <-ctx.Context().Done():
 		default:
@@ -121,7 +124,6 @@ func (env *Environment) BroadcastTxCommit(ctx *rpctypes.Context, tx types.Tx) (*
 
 	select {
 	case <-ctx.Context().Done():
-		reqRes.Done() // release waiter on goroutine
 		return nil, ErrTxBroadcast{Source: ctx.Context().Err(), ErrReason: ErrConfirmationNotReceived}
 	case checkTxRes := <-checkTxResCh:
 		if checkTxRes.Code != abci.CodeTypeOK {
```
