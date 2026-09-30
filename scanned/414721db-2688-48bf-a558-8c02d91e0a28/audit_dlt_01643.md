# [?] rpc: protect subscription access from race condition (#3910)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2019-08-22
Source: https://github.com/cometbft/cometbft/commit/7b2d018f847e9d97a8c0901641fb6405b03481dd
Type: security-commit

## Details
rpc: protect subscription access from race condition (#3910)

When using the RPC client in my test suite (with -race enabled), I do a lot of Subscribe/Unsubscribe operations, at some point (randomly) the race detector returns the following warning:

WARNING: DATA RACE
Read at 0x00c0009dbe30 by goroutine 31:
runtime.mapiterinit()
/usr/local/go/src/runtime/map.go:804 +0x0
github.com/tendermint/tendermint/rpc/client.(*WSEvents).redoSubscriptionsAfter()
/go/pkg/mod/github.com/tendermint/tendermint@v0.31.5/rpc/client/httpclient.go:364 +0xc0
github.com/tendermint/tendermint/rpc/client.(*WSEvents).eventListener()
/go/pkg/mod/github.com/tendermint/tendermint@v0.31.5/rpc/client/httpclient.go:393 +0x3c6 

Turns out that the redoSubscriptionAfter is not protecting the access to subscriptions.

The following change protects the read access to the subscription map behind the mutex

## Patch
### CHANGELOG_PENDING.md
```diff
@@ -28,3 +28,4 @@ program](https://hackerone.com/tendermint).
 
 - [config] \#3868 move misplaced `max_msg_bytes` into mempool section
 - [store] \#3893 register block amino, not just crypto
+- [rpc] [\#3910](https://github.com/tendermint/tendermint/pull/3910) protect subscription access from race conditions (@gchaincl)
```

### rpc/client/httpclient.go
```diff
@@ -453,6 +453,8 @@ func (w *WSEvents) UnsubscribeAll(ctx context.Context, subscriber string) error
 func (w *WSEvents) redoSubscriptionsAfter(d time.Duration) {
 	time.Sleep(d)
 
+	w.mtx.RLock()
+	defer w.mtx.RUnlock()
 	for q := range w.subscriptions {
 		err := w.ws.Subscribe(context.Background(), q)
 		if err != nil {
```
