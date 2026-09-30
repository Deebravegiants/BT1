# [?] fix(fibre): reject nil shard in UploadShard and recover handler panics (#7459)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-06-24
Source: https://github.com/celestiaorg/celestia-app/commit/c921190892fc1bcb37bd7af6598727daa05178df
Type: security-commit

## Details
fix(fibre): reject nil shard in UploadShard and recover handler panics (#7459)

## Problem

A peer with a valid funded Fibre payment promise can send `UploadShard`
with the `Shard` field omitted. `UploadShard` calls `verifyAssignment`
**before** `verifyShard`, and `verifyAssignment` dereferences
`shard.Rows` (`fibre/server_upload.go:167`), so a nil shard caused an
unrecovered nil-pointer panic. With no panic-recovery interceptor on the
Fibre gRPC server, the panic crashed the whole process — a cheap,
repeatable remote DoS of any Fibre validator's upload service.

Fibre-only; not a consensus or default-binary issue.

## Fix

- Reject a nil `req.Shard` with `InvalidArgument` before any
dereference.
- Add an always-on panic-recovery unary interceptor to the Fibre gRPC
server (defense in depth, recommended by the report): any handler panic
becomes an `Internal` error instead of crashing the process.

## Tests

- `TestServerUploadShard/NilShard` — panics on unpatched code, passes
after the fix.
- `TestRecoverUnaryInterceptor` /
`TestRecoverUnaryInterceptorPassthrough` — interceptor converts panics
to `Internal` and leaves normal calls untouched.

Closes PROTOCO-2004

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.8 <noreply@anthropic.com>

## Patch
### fibre/internal/grpc/server.go
```diff
@@ -3,10 +3,14 @@ package grpc
 import (
 	"context"
 	"fmt"
+	"log/slog"
 	"net"
+	"runtime/debug"
 
 	"github.com/celestiaorg/celestia-app/v9/x/fibre/types"
 	"google.golang.org/grpc"
+	"google.golang.org/grpc/codes"
+	"google.golang.org/grpc/status"
 )
 
 // Server wraps a [grpc.Server] with TCP listener and lifecycle management.
@@ -30,11 +34,32 @@ func Listen(listenAddr string) (*Server, error) {
 
 // Register builds the underlying [grpc.Server] with opts and registers the
 // fibre service. It must be called exactly once before [Server.Serve].
+//
+// A panic-recovery interceptor is always installed as defense in depth: a
+// panic in any handler (e.g. a malformed request that slips past validation)
+// is converted into an Internal gRPC error instead of crashing the process.
 func (s *Server) Register(service types.FibreServer, opts ...grpc.ServerOption) {
+	opts = append(opts, grpc.ChainUnaryInterceptor(recoverUnaryInterceptor))
 	s.server = grpc.NewServer(opts...)
 	types.RegisterFibreServer(s.server, service)
 }
 
+// recoverUnaryInterceptor recovers from panics in unary handlers and returns an
+// Internal error so a single malformed request cannot crash the server process.
+func recoverUnaryInterceptor(ctx context.Context, req any, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (resp any, err error) {
+	defer func() {
+		if r := recover(); r != nil {
+			slog.Error("recovered from panic in gRPC handler",
+				"method", info.FullMethod,
+				"panic", r,
+				"stack", string(debug.Stack()),
+			)
+			err = status.Errorf(codes.Internal, "internal error")
+		}
+	}()
+	return handler(ctx, req)
+}
+
 // ListenAddress returns the actual address the server is listening on.
 func (s *Server) ListenAddress() string {
 	return s.listener.Addr().String()
```

### fibre/internal/grpc/server_recovery_test.go
```diff
@@ -0,0 +1,40 @@
+package grpc
+
+import (
+	"context"
+	"testing"
+
+	"github.com/stretchr/testify/require"
+	"google.golang.org/grpc"
+	"google.golang.org/grpc/codes"
+	"google.golang.org/grpc/status"
+)
+
+// TestRecoverUnaryInterceptor ensures a panic in a handler is converted into an
+// Internal gRPC error rather than propagating up and crashing the process.
+func TestRecoverUnaryInterceptor(t *testing.T) {
+	info := &grpc.UnaryServerInfo{FullMethod: "/test/Panic"}
+	panicking := func(context.Context, any) (any, error) {
+		panic("boom")
+	}
+
+	require.NotPanics(t, func() {
+		resp, err := recoverUnaryInterceptor(context.Background(), nil, info, panicking)
+		require.Nil(t, resp)
+		require.Error(t, err)
+		require.Equal(t, codes.Internal, status.Code(err))
+	})
+}
+
+// TestRecoverUnaryInterceptorPassthrough ensures non-panicking handlers are
+// unaffected.
+func TestRecoverUnaryInterceptorPassthrough(t *testing.T) {
+	info := &grpc.UnaryServerInfo{FullMethod: "/test/Ok"}
+	ok := func(context.Context, any) (any, error) {
+		return "ok", nil
+	}
+
+	resp, err := recoverUnaryInterceptor(context.Background(), nil, info, ok)
+	require.NoError(t, err)
+	require.Equal(t, "ok", resp)
+}
```

### fibre/server_upload.go
```diff
@@ -37,6 +37,17 @@ func (s *Server) UploadShard(ctx context.Context, req *types.UploadShardRequest)
 	uploadSize = int64(promise.UploadSize)
 	log := s.log.With("blob_commitment", promise.Commitment.String(), "promise_height", promise.Height)
 
+	// validate request shape before verifyAssignment/verifyShard dereference
+	// the shard. A peer can send UploadShard with the Shard field omitted,
+	// which would otherwise cause a nil-pointer panic in the handler.
+	if req.Shard == nil {
+		err := errors.New("shard is required")
+		log.WarnContext(ctx, "missing shard in upload request", "error", err)
+		span.RecordError(err)
+		span.SetStatus(codes.Error, "missing shard in upload request")
+		return nil, status.Error(grpccodes.InvalidArgument, err.Error())
+	}
+
 	span.AddEvent("promise_verified", trace.WithAttributes(
 		attribute.String("promise_hash", hex.EncodeToString(promiseHash)),
 		attribute.String("blob_commitment", promise.Commitment.String()),
```

### fibre/server_upload_test.go
```diff
@@ -130,6 +130,19 @@ func TestServerUploadShard(t *testing.T) {
 				require.Error(t, err)
 			},
 		},
+		{
+			name: "NilShard",
+			requestModifier: func(req *types.UploadShardRequest) {
+				// omit the entire Shard message (a peer can send UploadShard
+				// with the Shard field unset). The handler must reject this
+				// gracefully rather than panicking on a nil dereference.
+				req.Shard = nil
+			},
+			check: func(t *testing.T, resp *types.UploadShardResponse, err error) {
+				require.Error(t, err)
+				require.Nil(t, resp)
+			},
+		},
 		{
 			name: "InvalidUploadSize",
 			requestModifier: func(req *types.UploadShardRequest) {
```
