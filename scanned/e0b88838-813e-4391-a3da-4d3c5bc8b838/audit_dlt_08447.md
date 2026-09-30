# [?] fix(test): fix data race during app and node startups (#5007)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2026-05-21
Source: https://github.com/celestiaorg/celestia-node/commit/5e07ff250c3b5986ce5186066852d173dfe31fb7
Type: security-commit

## Details
fix(test): fix data race during app and node startups (#5007)

## Patch
### core/testing.go
```diff
@@ -50,6 +50,12 @@ func StartTestNode(t *testing.T) testnode.Context {
 // StartTestNodeWithConfig starts Tendermint and Celestia App tandem with custom configuration.
 func StartTestNodeWithConfig(t *testing.T, cfg *testnode.Config) testnode.Context {
 	cctx, _, _ := testnode.NewNetwork(t, cfg)
+	// Wait until the chain has produced a block before returning; without this,
+	// callers that immediately query the chain (e.g. CoreAccessor.Start →
+	// GetNodeInfo) race the first block and fail with "celestia-app is not
+	// ready". Mirrors the pattern in state/txclient/testing.go.
+	_, err := cctx.WaitForHeight(int64(2))
+	require.NoError(t, err)
 	// we want to test over remote http client,
 	// so we are as close to the real environment as possible,
 	// however, it might be useful to use a local tendermint client
@@ -60,6 +66,10 @@ func StartTestNodeWithConfig(t *testing.T, cfg *testnode.Config) testnode.Contex
 // StartTestNodeWithConfigAndClient initializes a test node with default configuration and a WebSocket HTTP client.
 func StartTestNodeWithConfigAndClient(t *testing.T) (testnode.Context, *cmthttp.HTTP) {
 	cctx, rpcAddr, _ := testnode.NewNetwork(t, DefaultTestConfig())
+	// Mirror StartTestNodeWithConfig: wait until the chain has produced a
+	// block so callers do not race the first block.
+	_, err := cctx.WaitForHeight(int64(2))
+	require.NoError(t, err)
 	wsClient, err := cmthttp.New(rpcAddr, "/websocket")
 	if err != nil {
 		panic(err)
```

### state/core_access.go
```diff
@@ -4,6 +4,7 @@ import (
 	"context"
 	"errors"
 	"fmt"
+	"strings"
 	"sync"
 	"time"
 
@@ -24,6 +25,7 @@ import (
 	"go.opentelemetry.io/otel/attribute"
 	"go.opentelemetry.io/otel/trace"
 	"google.golang.org/grpc"
+	"google.golang.org/grpc/status"
 
 	"github.com/celestiaorg/celestia-app/v9/pkg/appconsts"
 	"github.com/celestiaorg/celestia-app/v9/pkg/user"
@@ -32,6 +34,7 @@ import (
 
 	"github.com/celestiaorg/celestia-node/header"
 	"github.com/celestiaorg/celestia-node/libs/utils"
+	"github.com/celestiaorg/celestia-node/nodebuilder/p2p"
 	"github.com/celestiaorg/celestia-node/state/txclient"
 )
 
@@ -128,7 +131,7 @@ func (ca *CoreAccessor) Start(ctx context.Context) error {
 	ca.feeGrantCli = feegrant.NewQueryClient(ca.coreConn)
 	// create ABCI query client
 	ca.abciQueryCli = tmservice.NewServiceClient(ca.coreConn)
-	resp, err := ca.abciQueryCli.GetNodeInfo(ctx, &tmservice.GetNodeInfoRequest{})
+	resp, err := waitForAppReady(ctx, ca.abciQueryCli)
 	if err != nil {
 		return fmt.Errorf("failed to get node info: %w", err)
 	}
@@ -589,3 +592,31 @@ func convertToSdkTxResponse(resp *user.TxResponse) *TxResponse {
 		Height: resp.Height,
 	}
 }
+
+func waitForAppReady(ctx context.Context, cli tmservice.ServiceClient) (*tmservice.GetNodeInfoResponse, error) {
+	for {
+		resp, err := cli.GetNodeInfo(ctx, &tmservice.GetNodeInfoRequest{})
+		if err == nil {
+			return resp, nil
+		}
+		if !isAppNotReady(err) {
+			return nil, err // wrong network / auth / dial — fail fast
+		}
+		select {
+		case <-time.After(p2p.BlockTime):
+		case <-ctx.Done():
+			return nil, fmt.Errorf("celestia-app not ready: %w", err)
+		}
+	}
+}
+
+// isAppNotReady matches celestia-app's "please wait for first block" startup
+// signal — sdk codespace "sdk" code 26 (ErrInvalidHeight) thrown by ABCIInfo
+// before the app multistore commits.
+func isAppNotReady(err error) bool {
+	s, ok := status.FromError(err)
+	if !ok {
+		return false
+	}
+	return strings.Contains(s.Message(), "please wait for first block")
+}
```
