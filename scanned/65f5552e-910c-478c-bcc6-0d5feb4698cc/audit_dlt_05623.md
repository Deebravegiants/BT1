# [?] rpc: fix handle batch deadlock (#22443)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-14
Source: https://github.com/erigontech/erigon/commit/c9d9061679963b91137f34cf1b475ce6142a5bb0
Type: security-commit

## Details
rpc: fix handle batch deadlock (#22443)

fixes #22424

Fix: wg.Add(len(calls)), matching the counter to the goroutines actually
spawned.
Added rpc/testdata/reqresp-batch-filtered.js using TDD (RED->GREEN)

## Patch
### rpc/handler.go
```diff
@@ -202,12 +202,12 @@ func (h *handler) handleBatch(msgs []*jsonrpcMessage) {
 		// see withoutGzipStreamingHook for why the hook must not reach them.
 		cp.ctx = withoutGzipStreamingHook(cp.ctx)
 		// All goroutines will place results right to this array. Because requests order must match reply orders.
-		answersWithNils := make([][]byte, len(msgs))
+		answersWithNils := make([][]byte, len(calls))
 		// Bounded parallelism pattern explanation https://blog.golang.org/pipelines#TOC_9.
 		boundedConcurrency := make(chan struct{}, h.maxBatchConcurrency)
 		defer close(boundedConcurrency)
 		wg := sync.WaitGroup{}
-		wg.Add(len(msgs))
+		wg.Add(len(calls))
 		for i := range calls {
 			boundedConcurrency <- struct{}{}
 			go func(i int) {
```

### rpc/testdata/reqresp-batch-filtered.js
```diff
@@ -0,0 +1,9 @@
+// A batch mixing a real call with a response-shaped message must still reply to the real call.
+
+--> [{"jsonrpc":"2.0","id":1,"method":"test_echo","params":["x",1]},{"jsonrpc":"2.0","id":2,"result":"0x1"}]
+<-- [{"jsonrpc":"2.0","id":1,"result":{"String":"x","Int":1,"Args":null}}]
+
+// A batch mixing a real call with a subscription notification must still reply to the real call.
+
+--> [{"jsonrpc":"2.0","id":3,"method":"test_echo","params":["x",2]},{"jsonrpc":"2.0","method":"eth_subscription","params":{"subscription":"0x1","result":"0x1"}}]
+<-- [{"jsonrpc":"2.0","id":3,"result":{"String":"x","Int":2,"Args":null}}]
```
