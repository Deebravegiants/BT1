# [?] rpc, node: fix nil-pointer panic in gzip batch flush race (#22338)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-09
Source: https://github.com/erigontech/erigon/commit/63cc7de5f83fbce21036eb4b0e7ecc922717c413
Type: security-commit

## Details
rpc, node: fix nil-pointer panic in gzip batch flush race (#22338)

## Summary

A JSON-RPC batch containing 2+ streamable methods ran each call on its
own goroutine, and each one invoked the shared gzip-streaming flush hook
installed on the request context. `gzipResponseWriter.Flush` is not safe
for concurrent use, so calling it from multiple goroutines raced on the
underlying `gzip.Writer` and could dereference a nil flate compressor,
crashing the node.

Batch sub-calls write into private per-item buffers rather than the HTTP
response writer, so the hook was never useful there in the first place.
Mask it out of the context used by batch sub-call goroutines instead of
hardening `gzipResponseWriter` itself, since it remains owned by a
single goroutine everywhere else.

Also hardens the hook mechanism itself: `WithGzipStreamingHook` now
panics if ever called with a nil hook, and `runMethod` guards the flush
call with `ok && flush != nil`, so the mechanism doesn't rely on the
hook always being stored as an untyped nil to stay safe.

Fixes #22334

## Tests

- Added `node/rpcstack_gzip_batch_race_test.go`
(`TestGzipHandlerBatchConcurrentStreamableFlush`): sends a real JSON-RPC
batch of 8 calls to a streamable method through the actual gzip
middleware and `rpc.Server`, with `Accept-Encoding: gzip`, and each
call's payload sized above `minGzipBodySize` so the fixed path still
gzips. Asserts `HTTP 200`, `Content-Encoding: gzip`, and that the
decoded batch contains all `n` responses with the expected ids/results —
not just reliance on `-race` to catch a regression. Before the fix,
running it with `-race` reliably reproduced both the data race and, on
some runs, the exact nil-pointer panic reported in the issue. After the
fix it passes cleanly and repeatably under `-race` (verified over 15
consecutive runs).
- Added `rpc/http_test.go` (`TestWithGzipStreamingHookPanicsOnNilHook`):
pins that `WithGzipStreamingHook` panics when given a nil hook.
- Added `rpc/handler_test.go` (`TestRunMethodFlushHookNilFunc`): pins
that `runMethod` does not panic when the hook stored on the context is a
typed nil `func()` rather than an untyped nil.
- Full `rpc/...` and `node/...` suites pass with `-race`.

### Manual end-to-end verification

Also reproduced the issue against two real running nodes, one built from
this branch's parent commit and one from this branch, both sent the
exact same JSON-RPC batch (16 calls to `debug_traceBlockByNumber`) with
`Accept-Encoding: gzip`:

- **Pre-fix binary**: crashed on the first request, with a panic
identical to the one reported in the issue (`flate.(*Writer).Flush` →
`gzip.(*Writer).Flush` → `gzipResponseWriter.Flush` → `runMethod` →
`handleCall` → `handleCallMsg` → `handleBatch`).
- **Fixed binary**: the same request succeeded (`HTTP 200`, correct JSON
body) across 8 consecutive attempts, node stayed up and kept producing
blocks throughout.

## Test plan

- [x] `go test -race -run TestGzipHandlerBatchConcurrentStreamableFlush
./node/...`
- [x] `go test -race -count=1 ./rpc/... ./node/...`
- [x] `make lint`
- [x] Manual repro against a real node: pre-fix binary crashes, fixed
binary doesn't

## Note

A pre-existing deadlock in `handleBatch` (`wg.Add(len(msgs))` vs.
`len(calls)` goroutines spawned) was flagged during review. It's
unrelated to the gzip race fixed here and will be addressed in a
separate PR.

### node/rpcstack_gzip_batch_race_test.go
```diff
@@ -0,0 +1,83 @@
+// Copyright 2026 The Erigon Authors
+// This file is part of Erigon.
+//
+// Erigon is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// Erigon is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with Erigon. If not, see <http://www.gnu.org/licenses/>.
+
+package node
+
+import (
+	"encoding/json"
+	"fmt"
+	"net/http"
+	"net/http/httptest"
+	"strings"
+	"testing"
+
+	"github.com/stretchr/testify/assert"
+	"github.com/stretchr/testify/require"
+
+	"github.com/erigontech/erigon/rpc/jsonstream"
+)
+
+// gzipBatchStreamingService exposes a streamable method (last arg jsonstream.Stream) so
+// that runMethod invokes the gzip-streaming hook, per rpc/service.go's streamable detection.
+type gzipBatchStreamingService struct{}
+
+func (gzipBatchStreamingService) Echo(s string, stream jsonstream.Stream) error {
+	stream.WriteString(s)
+	return nil
+}
+
+// TestGzipHandlerBatchConcurrentStreamableFlush reproduces a batch of streamable calls each
+// running on its own goroutine (rpc/handler.go handleBatch), where every goroutine invokes
+// the gzip-streaming flush hook installed on the shared request context. gzipResponseWriter.
+// Flush is not safe for concurrent use, so calling it from multiple goroutines races on the
+// underlying gzip.Writer and can dereference a nil flate compressor. Run with -race to
+// observe the race (or a direct panic/crash from an unrecovered panic in a batch goroutine).
+func TestGzipHandlerBatchConcurrentStreamableFlush(t *testing.T) {
+	srv := newTestRPCServer(t)
+	require.NoError(t, srv.RegisterName("test", gzipBatchStreamingService{}))
+
+	handler := newGzipHandler(srv)
+
+	const n = 8
+	echoArg := strings.Repeat("x", 256) // large enough that the batch response exceeds minGzipBodySize
+	calls := make([]string, n)
+	for i := range calls {
+		calls[i] = fmt.Sprintf(`{"jsonrpc":"2.0","id":%d,"method":"test_echo","params":["%s"]}`, i+1, echoArg)
+	}
+	reqBody := "[" + strings.Join(calls, ",") + "]"
+
+	req := httptest.NewRequest(http.MethodPost, "/", strings.NewReader(reqBody))
+	req.Header.Set("Content-Type", "application/json")
+	req.Header.Set("Accept-Encoding", "gzip")
+	rec := httptest.NewRecorder()
+
+	handler.ServeHTTP(rec, req)
+
+	require.Equal(t, http.StatusOK, rec.Code)
+	assert.Equal(t, "gzip", rec.Header().Get("Content-Encoding"))
+
+	respBody := decompressGzip(t, rec.Body)
+	var respBatch []struct {
+		ID     int    `json:"id"`
+		Result string `json:"result"`
+	}
+	require.NoError(t, json.Unmarshal(respBody, &respBatch))
+	require.Len(t, respBatch, n)
+	for i, resp := range respBatch {
+		assert.Equal(t, i+1, resp.ID)
+		assert.Equal(t, echoArg, resp.Result)
+	}
+}
```

### rpc/handler.go
```diff
@@ -198,6 +198,9 @@ func (h *handler) handleBatch(msgs []*jsonrpcMessage) {
 
 	// Process calls on a goroutine because they may block indefinitely:
 	h.startCallProc(func(cp *callProc) {
+		// Batch items below run concurrently and write into private per-item buffers;
+		// see withoutGzipStreamingHook for why the hook must not reach them.
+		cp.ctx = withoutGzipStreamingHook(cp.ctx)
 		// All goroutines will place results right to this array. Because requests order must match reply orders.
 		answersWithNils := make([][]byte, len(msgs))
 		// Bounded parallelism pattern explanation https://blog.golang.org/pipelines#TOC_9.
@@ -650,7 +653,7 @@ func (h *handler) runMethod(ctx context.Context, msg *jsonrpcMessage, callb *cal
 	}
 
 	// Switch gzip middleware to streaming mode before writing any response data.
-	if flush, ok := ctx.Value(httpFlusherContextKey{}).(func()); ok {
+	if flush, ok := ctx.Value(httpFlusherContextKey{}).(func()); ok && flush != nil {
 		flush()
 	}
 
```

### rpc/handler_test.go
```diff
@@ -138,3 +138,42 @@ func TestHandlerDoesNotDoubleWriteNull(t *testing.T) {
 	}
 
 }
+
+// TestRunMethodFlushHookNilFunc pins the invariant that runMethod must not panic when the
+// gzip-streaming hook stored on the context is a typed nil func(), not just an untyped nil.
+// The normal masking path (withoutGzipStreamingHook) stores an untyped nil so the type
+// assertion fails outright, but runMethod's guard should not depend on callers always doing
+// that correctly.
+func TestRunMethodFlushHookNilFunc(t *testing.T) {
+	msg := jsonrpcMessage{
+		Version: "2.0",
+		ID:      []byte{49},
+		Method:  "test_test",
+		Params:  []byte("[]"),
+	}
+
+	dummyFunc := func(stream jsonstream.Stream) error {
+		stream.WriteEmptyObject()
+		return nil
+	}
+
+	cb := &callback{
+		fn:         reflect.ValueOf(dummyFunc),
+		streamable: true,
+	}
+
+	args, err := parsePositionalArguments(msg.Params, cb.argTypes)
+	if err != nil {
+		t.Fatal(err)
+	}
+
+	ctx := context.WithValue(context.Background(), httpFlusherContextKey{}, (func())(nil))
+
+	var buf bytes.Buffer
+	stream := jsonstream.New(jsoniter.NewStream(jsoniter.ConfigDefault, &buf, 4096))
+
+	h := handler{}
+	assert.NotPanics(t, func() {
+		h.runMethod(ctx, &msg, cb, args, stream)
+	})
+}
```

### rpc/http.go
```diff
@@ -251,9 +251,20 @@ type httpFlusherContextKey struct{}
 // writing the first byte of a streamable response, switching the gzip middleware from
 // one-shot buffering to incremental streaming. Must only be called by the gzip middleware.
 func WithGzipStreamingHook(ctx context.Context, hook func()) context.Context {
+	if hook == nil {
+		panic("rpc: WithGzipStreamingHook called with a nil hook")
+	}
 	return context.WithValue(ctx, httpFlusherContextKey{}, hook)
 }
 
+// withoutGzipStreamingHook masks any gzip-streaming hook set on an ancestor context. Batch
+// sub-calls write into a private per-item buffer rather than the HTTP response writer, so
+// the hook must not fire for them; calling it concurrently from multiple batch goroutines is
+// unsafe, since the underlying gzip.Writer it activates is not safe for concurrent use.
+func withoutGzipStreamingHook(ctx context.Context) context.Context {
+	return context.WithValue(ctx, httpFlusherContextKey{}, nil)
+}
+
 func withOverloadedFlag(ctx context.Context) (context.Context, *bool) {
 	flag := new(bool)
 	return context.WithValue(ctx, httpOverloadedKey{}, flag), flag
```

### rpc/http_test.go
```diff
@@ -20,6 +20,7 @@
 package rpc
 
 import (
+	"context"
 	"encoding/json"
 	"io"
 	"net/http"
@@ -223,3 +224,13 @@ func TestHTTPPeerInfo(t *testing.T) {
 		t.Errorf("wrong HTTP.Origin %q", info.HTTP.UserAgent)
 	}
 }
+
+// TestWithGzipStreamingHookPanicsOnNilHook pins the write-side contract of the gzip-streaming
+// hook mechanism: WithGzipStreamingHook must never store a nil hook, since a typed-nil func()
+// stored under httpFlusherContextKey silently disables gzip streaming instead of activating it.
+// Misuse must fail loudly here rather than degrade quietly at the runMethod call site.
+func TestWithGzipStreamingHookPanicsOnNilHook(t *testing.T) {
+	require.Panics(t, func() {
+		WithGzipStreamingHook(context.Background(), nil)
+	})
+}
```
