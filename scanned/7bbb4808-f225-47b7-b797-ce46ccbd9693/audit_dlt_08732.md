# [?] op-e2e: Fix panics in logging (#15521)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2025-04-23
Source: https://github.com/ethereum-optimism/optimism/commit/6d9d43cb6f2721c9638be9fe11d261c0602beb54
Type: security-commit

## Details
op-e2e: Fix panics in logging (#15521)

* op-e2e: Don't set the root logger in tests.

* op-e2e: Fix thread safety in test logger

## Patch
### op-e2e/interop/interop_test.go
```diff
@@ -12,7 +12,6 @@ import (
 	"github.com/ethereum-optimism/optimism/op-challenger/game/fault/contracts/metrics"
 	"github.com/ethereum-optimism/optimism/op-service/dial"
 	"github.com/ethereum-optimism/optimism/op-service/eth"
-	oplog "github.com/ethereum-optimism/optimism/op-service/log"
 	"github.com/ethereum-optimism/optimism/op-service/sources/batching"
 	"github.com/ethereum-optimism/optimism/op-service/testlog"
 	"github.com/ethereum/go-ethereum/ethclient"
@@ -253,8 +252,6 @@ func TestInterop_EmitLogs(t *testing.T) {
 
 func TestInteropBlockBuilding(t *testing.T) {
 	t.Parallel()
-	logger := testlog.Logger(t, log.LevelInfo)
-	oplog.SetGlobalLogHandler(logger.Handler())
 
 	test := func(t *testing.T, s2 SuperSystem) {
 		ids := s2.L2IDs()
```

### op-service/testlog/testlog.go
```diff
@@ -22,6 +22,7 @@ import (
 	"bytes"
 	"context"
 	"fmt"
+	"io"
 	"log/slog"
 	"os"
 	"path"
@@ -60,7 +61,7 @@ type logger struct {
 	t   Testing
 	l   log.Logger
 	mu  *sync.Mutex
-	buf *bytes.Buffer
+	buf *syncBuffer
 }
 
 // Logger returns a logger which logs to the unit test log of t.
@@ -69,7 +70,9 @@ func Logger(t Testing, level slog.Level) log.Logger {
 }
 
 func LoggerWithHandlerMod(t Testing, level slog.Level, handlerMod func(slog.Handler) slog.Handler) log.Logger {
-	l := &logger{t: t, mu: new(sync.Mutex), buf: new(bytes.Buffer)}
+	// We use a sync wrapper around the buffer because it potentially gets passed into a handler later which can then
+	// be retrieved using `Handler()` so it isn't guaranteed to always be guarded by the logger mutex.
+	l := &logger{t: t, mu: new(sync.Mutex), buf: newSyncBuffer(new(bytes.Buffer))}
 
 	var handler slog.Handler
 	if outdir := os.Getenv("OP_TESTLOG_FILE_LOGGER_OUTDIR"); outdir != "" {
@@ -103,7 +106,10 @@ func fileHandler(t Testing, outdir string, level slog.Level) slog.Handler {
 			return
 		}
 
-		rootHdlr := log.NewTerminalHandlerWithLevel(bufio.NewWriter(f), level, false)
+		// The writer needs to be thread safe as it might be passed through to a different TerminalHandler instance
+		// if rootHdlr.WithAttrs ever winds up being called.
+		writer := newSyncWriter(bufio.NewWriter(f))
+		rootHdlr := log.NewTerminalHandlerWithLevel(writer, level, false)
 		oplog.SetGlobalLogHandler(rootHdlr)
 		t.Logf("redirecting root logger to %s", f.Name())
 	})
@@ -311,3 +317,48 @@ func (w *deferredWriter) Close() error {
 	}
 	return w.close()
 }
+
+type buffer interface {
+	io.Writer
+	io.Reader
+	Reset()
+}
+
+type syncWriter struct {
+	mu sync.Mutex
+	w  io.Writer
+}
+
+func newSyncWriter(w io.Writer) *syncWriter {
+	return &syncWriter{w: w}
+}
+
+func (w *syncWriter) Write(p []byte) (n int, err error) {
+	w.mu.Lock()
+	defer w.mu.Unlock()
+	return w.w.Write(p)
+}
+
+type syncBuffer struct {
+	syncWriter
+	b buffer
+}
+
+func newSyncBuffer(b buffer) *syncBuffer {
+	return &syncBuffer{
+		syncWriter: syncWriter{w: b},
+		b:          b,
+	}
+}
+
+func (b *syncBuffer) Read(p []byte) (n int, err error) {
+	b.mu.Lock()
+	defer b.mu.Unlock()
+	return b.b.Read(p)
+}
+
+func (b *syncBuffer) Reset() {
+	b.mu.Lock()
+	defer b.mu.Unlock()
+	b.b.Reset()
+}
```
