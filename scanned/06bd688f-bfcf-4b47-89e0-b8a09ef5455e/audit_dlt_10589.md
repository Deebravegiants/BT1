# [?] fix(bug): Startup race condition fix (#596)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2024-03-21
Source: https://github.com/berachain/beacon-kit/commit/f910e29227a47d3679e6397788051bbe74bdbd89
Type: security-commit

## Details
fix(bug): Startup race condition fix (#596)

* bet

* lint

## Patch
### beacon/sync/service.go
```diff
@@ -33,7 +33,6 @@ import (
 	"github.com/berachain/beacon-kit/engine/client"
 	"github.com/berachain/beacon-kit/runtime/service"
 	"github.com/cockroachdb/errors"
-	cosmosclient "github.com/cosmos/cosmos-sdk/client"
 	"github.com/sourcegraph/conc"
 )
 
@@ -46,8 +45,8 @@ const syncLoopInterval = 5 * time.Second
 type Service struct {
 	service.BaseService
 	engineClient *client.EngineClient
-	clientCtx    *cosmosclient.Context
-	cfg          *Config
+	// clientCtx    *cosmosclient.Context
+	cfg *Config
 
 	isInitSync        bool
 	isSyncedLock      *sync.RWMutex
@@ -59,14 +58,6 @@ type Service struct {
 	clNumPeers        uint64
 }
 
-// SetClientContext sets the client context for the service.
-func (s *Service) SetClientContext(clientCtx cosmosclient.Context) {
-	if s == nil {
-		panic("service is nil")
-	}
-	s.clientCtx = &clientCtx
-}
-
 // Start initiates the synchronization service.
 func (s *Service) Start(ctx context.Context) {
 	s.isSyncedLock = &sync.RWMutex{}
```

### beacon/sync/sync.go
```diff
@@ -27,33 +27,31 @@ package sync
 
 import (
 	"context"
-
-	"github.com/cometbft/cometbft/rpc/client"
 )
 
 // CheckELSync checks if the execution layer is syncing.
-func (s *Service) CheckCLSync(ctx context.Context) {
+func (s *Service) CheckCLSync(_ context.Context) {
 	// Call the CometBFT Client to get the sync progress.
-	resultStatus, err := s.clientCtx.Client.Status(ctx)
-	s.isSyncedCond.L.Lock()
-	defer s.isSyncedCond.L.Unlock()
-	if err != nil {
-		s.isCLSynced = false
-		return
-	}
+	// resultStatus, err := s.clientCtx.Client.Status(ctx)
+	// s.isSyncedCond.L.Lock()
+	// defer s.isSyncedCond.L.Unlock()
+	// if err != nil {
+	// 	s.isCLSynced = false
+	// 	return
+	// }
 
-	// If we are not catchup, then say we are synced.
-	s.isCLSynced = !resultStatus.SyncInfo.CatchingUp
+	// // If we are not catchup, then say we are synced.
+	// s.isCLSynced = !resultStatus.SyncInfo.CatchingUp
 
-	// Add a log if syncing.
-	if !s.isCLSynced {
-		s.Logger().Warn(
-			"beacon client is attemping to sync.... ",
-			"current_beacon", resultStatus.SyncInfo.LatestBlockHeight,
-			"highest_beacon", resultStatus.SyncInfo.CatchingUp,
-			"starting_beacon", resultStatus.SyncInfo.EarliestBlockHeight,
-		)
-	}
+	// // Add a log if syncing.
+	// if !s.isCLSynced {
+	// 	s.Logger().Warn(
+	// 		"beacon client is attemping to sync.... ",
+	// 		"current_beacon", resultStatus.SyncInfo.LatestBlockHeight,
+	// 		"highest_beacon", resultStatus.SyncInfo.CatchingUp,
+	// 		"starting_beacon", resultStatus.SyncInfo.EarliestBlockHeight,
+	// 	)
+	// }
 }
 
 // CheckELSync checks if the execution layer is syncing.
@@ -83,17 +81,17 @@ func (s *Service) CheckELSync(ctx context.Context) {
 
 // UpdateNumCLPeers updates the number of peers connected at the consensus
 // layer.
-func (s *Service) UpdateNumCLPeers(ctx context.Context) {
-	// Call the CometBFT Client to get the sync progress.
-	netInfo, err := s.clientCtx.Client.(client.NetworkClient).NetInfo(ctx)
-	if err != nil {
-		s.clNumPeers = 0
-		return
-	}
+func (s *Service) UpdateNumCLPeers(_ context.Context) {
+	// // Call the CometBFT Client to get the sync progress.
+	// netInfo, err := s.clientCtx.Client.(client.NetworkClient).NetInfo(ctx)
+	// if err != nil {
+	// 	s.clNumPeers = 0
+	// 	return
+	// }
 
-	//#nosec:G701 // if our number of peers overflows a int64
-	// we have bigger problems.
-	s.clNumPeers = uint64(netInfo.NPeers)
+	// //#nosec:G701 // if our number of peers overflows a int64
+	// // we have bigger problems.
+	// s.clNumPeers = uint64(netInfo.NPeers)
 }
 
 // UpdateNumELPeers updates the number of peers connected at the execution
@@ -106,5 +104,5 @@ func (s *Service) UpdateNumELPeers(_ context.Context) {
 	// 	s.elNumPeers = 0
 	// 	return
 	// }
-	s.elNumPeers = 0
+	// s.elNumPeers = 0
 }
```

### config/cmd/config.go
```diff
@@ -44,7 +44,7 @@ func InitCometBFTConfig() *cmtcfg.Config {
 	consensus.TimeoutPropose = 3000 * time.Millisecond
 	consensus.TimeoutPrevote = 2000 * time.Millisecond
 	consensus.TimeoutPrecommit = 2000 * time.Millisecond
-	consensus.TimeoutCommit = 10000 * time.Millisecond
+	consensus.TimeoutCommit = 6000 * time.Millisecond
 
 	// BeaconKit forces PebbleDB as the database backend.
 	cfg.DBBackend = "pebbledb"
```

### examples/beacond/app/app.go
```diff
@@ -181,20 +181,12 @@ func NewBeaconKitApp(
 		panic(err)
 	}
 
-	return app
-}
-
-// PostStartup is called after the app has started up and CometBFT is connected.
-func (app *BeaconApp) PostStartup(
-	ctx context.Context,
-	clientCtx client.Context,
-) error {
 	// Initial check for execution client sync.
 	app.BeaconKitRuntime.StartServices(
-		ctx,
-		clientCtx,
+		context.Background(),
 	)
-	return nil
+
+	return app
 }
 
 // kvStoreKeys returns the KVStoreKeys for the app.
```

### examples/beacond/cmd/root/root.go
```diff
@@ -27,7 +27,6 @@
 package root
 
 import (
-	"context"
 	"io"
 	"os"
 
@@ -49,7 +48,6 @@ import (
 	"github.com/cosmos/cosmos-sdk/types/module"
 	"github.com/spf13/cobra"
 	"github.com/spf13/viper"
-	"golang.org/x/sync/errgroup"
 )
 
 // NewRootCmd creates a new root command for simd. It is called once in the main
@@ -134,13 +132,7 @@ func NewRootCmd() *cobra.Command {
 		clientCtx.Codec,
 		moduleBasicManager,
 		newApp,
-		func(
-			_app servertypes.Application,
-			svrCtx *server.Context, clientCtx client.Context, ctx context.Context, g *errgroup.Group,
-		) error {
-			return _app.(*app.BeaconApp).PostStartup(ctx, clientCtx)
-		},
-
+		nil,
 		appExport,
 	)
 
```

### runtime/runtime.go
```diff
@@ -50,7 +50,6 @@ import (
 	"github.com/berachain/beacon-kit/lib/abi"
 	_ "github.com/berachain/beacon-kit/runtime/maxprocs"
 	"github.com/berachain/beacon-kit/runtime/service"
-	"github.com/cosmos/cosmos-sdk/client"
 )
 
 // BeaconKitRuntime is a struct that holds the
@@ -222,12 +221,10 @@ func NewDefaultBeaconKitRuntime(
 // StartServices starts the services.
 func (r *BeaconKitRuntime) StartServices(
 	ctx context.Context,
-	clientCtx client.Context,
 ) {
 	var syncService *sync.Service
 	if err := r.services.FetchService(&syncService); err != nil {
 		panic(err)
 	}
-	syncService.SetClientContext(clientCtx)
 	r.services.StartAll(ctx)
 }
```
