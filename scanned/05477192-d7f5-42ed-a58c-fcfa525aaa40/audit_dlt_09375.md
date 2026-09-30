# [?] fix: resolve JWT authentication race condition on validator restart (#2937)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2025-12-02
Source: https://github.com/berachain/beacon-kit/commit/902f30065420772c1f8d9cef4abf03bdc1e78917
Type: security-commit

## Details
fix: resolve JWT authentication race condition on validator restart (#2937)

## Patch
### execution/client/client.go
```diff
@@ -22,6 +22,7 @@ package client
 
 import (
 	"context"
+	"fmt"
 	"math/big"
 	"sync"
 	"time"
@@ -68,6 +69,7 @@ func New(
 		cfg.RPCDialURL.String(),
 		jwtSecret,
 		cfg.RPCJWTRefreshInterval,
+		logger,
 	)
 
 	// Enforcing minimum rpc timeout
@@ -108,7 +110,12 @@ func (s *EngineClient) Name() string {
 
 // Start the engine client.
 func (s *EngineClient) Start(ctx context.Context) error {
-	// Start the Client.
+	// Initialize the JWT token before making any RPC calls
+	if err := s.Client.Initialize(); err != nil {
+		return fmt.Errorf("failed to initialize RPC client: %w", err)
+	}
+
+	// Start the Client background refresh loop.
 	go s.Client.Start(ctx)
 
 	s.logger.Info(
```

### execution/client/ethclient/engine_test.go
```diff
@@ -154,6 +154,7 @@ type stubRPCClient struct {
 	t *testing.T
 }
 
+func (tc *stubRPCClient) Initialize() error     { return nil }
 func (tc *stubRPCClient) Start(context.Context) {}
 func (tc *stubRPCClient) Call(_ context.Context, target any, _ string, _ ...any) error {
 	tc.t.Helper()
```

### execution/client/ethclient/rpc/client.go
```diff
@@ -29,6 +29,7 @@ import (
 	"sync"
 	"time"
 
+	"github.com/berachain/beacon-kit/log"
 	"github.com/berachain/beacon-kit/primitives/encoding/json"
 	beaconhttp "github.com/berachain/beacon-kit/primitives/net/http"
 	"github.com/berachain/beacon-kit/primitives/net/jwt"
@@ -37,6 +38,7 @@ import (
 var _ Client = (*client)(nil)
 
 type Client interface {
+	Initialize() error
 	Start(context.Context)
 	Call(ctx context.Context, target any, method string, params ...any) error
 	Close() error
@@ -56,6 +58,8 @@ type client struct {
 	// jwtRefreshInterval is the interval at which the JWT token should be
 	// refreshed.
 	jwtRefreshInterval time.Duration
+	// logger is the logger for the RPC client.
+	logger log.Logger
 
 	// mu protects header for concurrent access.
 	mu sync.RWMutex
@@ -69,6 +73,7 @@ func NewClient(
 	url string,
 	secret *jwt.Secret,
 	jwtRefreshInterval time.Duration,
+	logger log.Logger,
 ) Client {
 	rpc := &client{
 		url:    url,
@@ -84,6 +89,7 @@ func NewClient(
 		jwtSecret:          secret,
 		jwtRefreshInterval: jwtRefreshInterval,
 		header:             http.Header{"Content-Type": {"application/json"}},
+		logger:             logger,
 	}
 
 	return rpc
@@ -94,22 +100,30 @@ func (rpc *client) Start(ctx context.Context) {
 	ticker := time.NewTicker(rpc.jwtRefreshInterval)
 	defer ticker.Stop()
 
-	if err := rpc.updateHeader(); err != nil {
-		panic(err)
-	}
+	// Initial JWT update is done in Initialize() now
 	for {
 		select {
 		case <-ctx.Done():
 			return
 		case <-ticker.C:
 			if err := rpc.updateHeader(); err != nil {
-				// TODO: log or something.
+				rpc.logger.Error("Failed to refresh JWT token", "error", err)
 				continue
 			}
 		}
 	}
 }
 
+// Initialize sets up the initial JWT token. This should be called before
+// making any RPC calls to ensure a fresh token is available.
+func (rpc *client) Initialize() error {
+	rpc.logger.Info("Initializing RPC client with fresh JWT token")
+	if err := rpc.updateHeader(); err != nil {
+		return fmt.Errorf("failed to initialize JWT token: %w", err)
+	}
+	return nil
+}
+
 // Close closes the RPC client.
 func (rpc *client) Close() error {
 	rpc.client.CloseIdleConnections()
```
