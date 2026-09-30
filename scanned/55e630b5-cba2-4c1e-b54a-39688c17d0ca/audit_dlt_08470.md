# [?] [CORE-627] - Fix daemon panics by delaying daemon start until gRPC service is available (#437)

## Summary
Severity: Unknown
Chain: dYdX
Component: dydxprotocol/v4-chain
Published: 2023-10-03
Source: https://github.com/dydxprotocol/v4-chain/commit/0b4c3c489993265853d789930e485db1cc924676
Type: security-commit

## Details
[CORE-627] - Fix daemon panics by delaying daemon start until gRPC service is available (#437)

## Patch
### protocol/app/app.go
```diff
@@ -287,6 +287,12 @@ type App struct {
 
 	IndexerEventManager indexer_manager.IndexerEventManager
 	Server              *daemonserver.Server
+
+	// startDaemons encapsulates the logic that starts all daemons and daemon services. This function contains a
+	// closure of all relevant data structures that are shared with various keepers. Daemon services startup is
+	// delayed until after the gRPC service is initialized so that the gRPC service will be available and the daemons
+	// can correctly operate.
+	startDaemons func()
 }
 
 // assertAppPreconditions assert invariants required for an application to start.
@@ -567,70 +573,77 @@ func New(
 	bridgeEventManager := bridgedaemontypes.NewBridgeEventManager(timeProvider)
 	app.Server.WithBridgeEventManager(bridgeEventManager)
 
-	// Start server for handling gRPC messages from daemons.
-	go app.Server.Start()
+	// Create a closure for starting daemons and daemon server. Daemon services are delayed until after the gRPC
+	// service is started because daemons depend on the gRPC service being available. If a node is initialized
+	// with a genesis time in the future, then the gRPC service will not be available until the genesis time, the
+	// daemons will not be able to connect to the cosmos gRPC query service and finish initialization, and the daemon
+	// monitoring service will panic.
+	app.startDaemons = func() {
+		// Start server for handling gRPC messages from daemons.
+		go app.Server.Start()
+
+		// Start liquidations client for sending potentially liquidatable subaccounts to the application.
+		if daemonFlags.Liquidation.Enabled {
+			app.Server.ExpectLiquidationsDaemon(
+				daemonservertypes.MaximumAcceptableUpdateDelay(daemonFlags.Liquidation.LoopDelayMs),
+			)
+			go func() {
+				if err := liquidationclient.Start(
+					// The client will use `context.Background` so that it can have a different context from
+					// the main application.
+					context.Background(),
+					daemonFlags,
+					appFlags,
+					logger,
+					&lib.GrpcClientImpl{},
+				); err != nil {
+					panic(err)
+				}
+			}()
+		}
 
-	// Start liquidations client for sending potentially liquidatable subaccounts to the application.
-	if daemonFlags.Liquidation.Enabled {
-		app.Server.ExpectLiquidationsDaemon(
-			daemonservertypes.MaximumAcceptableUpdateDelay(daemonFlags.Liquidation.LoopDelayMs),
-		)
-		go func() {
-			if err := liquidationclient.Start(
+		// Non-validating full-nodes have no need to run the price daemon.
+		if !appFlags.NonValidatingFullNode && daemonFlags.Price.Enabled {
+			exchangeStartupConfig := configs.ReadExchangeStartupConfigFile(homePath)
+			app.Server.ExpectPricefeedDaemon(daemonservertypes.MaximumAcceptableUpdateDelay(daemonFlags.Price.LoopDelayMs))
+			// Start pricefeed client for sending prices for the pricefeed server to consume. These prices
+			// are retrieved via third-party APIs like Binance and then are encoded in-memory and
+			// periodically sent via gRPC to a shared socket with the server.
+			client := pricefeedclient.StartNewClient(
 				// The client will use `context.Background` so that it can have a different context from
 				// the main application.
 				context.Background(),
 				daemonFlags,
 				appFlags,
 				logger,
 				&lib.GrpcClientImpl{},
-			); err != nil {
-				panic(err)
-			}
-		}()
-	}
-
-	// Non-validating full-nodes have no need to run the price daemon.
-	if !appFlags.NonValidatingFullNode && daemonFlags.Price.Enabled {
-		exchangeStartupConfig := configs.ReadExchangeStartupConfigFile(homePath)
-		app.Server.ExpectPricefeedDaemon(daemonservertypes.MaximumAcceptableUpdateDelay(daemonFlags.Price.LoopDelayMs))
-		// Start pricefeed client for sending prices for the pricefeed server to consume. These prices
-		// are retrieved via third-party APIs like Binance and then are encoded in-memory and
-		// periodically sent via gRPC to a shared socket with the server.
-		client := pricefeedclient.StartNewClient(
-			// The client will use `context.Background` so that it can have a different context from
-			// the main application.
-			context.Background(),
-			daemonFlags,
-			appFlags,
-			logger,
-			&lib.GrpcClientImpl{},
-			exchangeStartupConfig,
-			constants.StaticExchangeDetails,
-			&pricefeedclient.SubTaskRunnerImpl{},
-		)
-		stoppable.RegisterServiceForTestCleanup(appFlags.GrpcAddress, client)
-	}
+				exchangeStartupConfig,
+				constants.StaticExchangeDetails,
+				&pricefeedclient.SubTaskRunnerImpl{},
+			)
+			stoppable.RegisterServiceForTestCleanup(appFlags.GrpcAddress, client)
+		}
 
-	// Start Bridge Daemon.
-	// Non-validating full-nodes have no need to run the bridge daemon.
-	if !appFlags.NonValidatingFullNode && daemonFlags.Bridge.Enabled {
-		// TODO(CORE-582): Re-enable bridge daemon registration once the bridge daemon is fixed in local / CI
-		// environments.
-		// app.Server.ExpectBridgeDaemon(daemonservertypes.MaximumAcceptableUpdateDelay(daemonFlags.Bridge.LoopDelayMs))
-		go func() {
-			if err := bridgeclient.Start(
-				// The client will use `context.Background` so that it can have a different context from
-				// the main application.
-				context.Background(),
-				daemonFlags,
-				appFlags,
-				logger,
-				&lib.GrpcClientImpl{},
-			); err != nil {
-				panic(err)
-			}
-		}()
+		// Start Bridge Daemon.
+		// Non-validating full-nodes have no need to run the bridge daemon.
+		if !appFlags.NonValidatingFullNode && daemonFlags.Bridge.Enabled {
+			// TODO(CORE-582): Re-enable bridge daemon registration once the bridge daemon is fixed in local / CI
+			// environments.
+			// app.Server.ExpectBridgeDaemon(daemonservertypes.MaximumAcceptableUpdateDelay(daemonFlags.Bridge.LoopDelayMs))
+			go func() {
+				if err := bridgeclient.Start(
+					// The client will use `context.Background` so that it can have a different context from
+					// the main application.
+					context.Background(),
+					daemonFlags,
+					appFlags,
+					logger,
+					&lib.GrpcClientImpl{},
+				); err != nil {
+					panic(err)
+				}
+			}()
+		}
 	}
 
 	app.PricesKeeper = *pricesmodulekeeper.NewKeeper(
@@ -1329,6 +1342,9 @@ func (app *App) RegisterAPIRoutes(apiSvr *api.Server, apiConfig config.APIConfig
 	if apiConfig.Swagger {
 		RegisterSwaggerAPI(clientCtx, apiSvr.Router)
 	}
+
+	// Now that the API server has been configured, start the daemons.
+	app.startDaemons()
 }
 
 // RegisterTxService implements the Application.RegisterTxService method.
```

### protocol/x/prices/keeper/market.go
```diff
@@ -74,17 +74,22 @@ func (k Keeper) CreateMarket(
 	return marketParam, nil
 }
 
-// IsRecentlyAdded returns true if the market was added recently. Since it takes a few seconds for
-// index prices to populate, we would not consider missing index prices for a recently added market
-// to be an error.
-func (k Keeper) IsRecentlyAdded(marketId uint32) bool {
+// IsRecentlyAvailable returns true if the market was recently made available to the pricefeed daemon. A market is
+// considered recently available either if it was recently created, or if the pricefeed daemon was recently started. If
+// an index price does not exist for a recently available market, the protocol does not consider this an error
+// condition, as it is expected that the pricefeed daemon will eventually provide a price for the market within a
+// few seconds.
+func (k Keeper) IsRecentlyAvailable(ctx sdk.Context, marketId uint32) bool {
 	createdAt, ok := k.marketToCreatedAt[marketId]
 
 	if !ok {
 		return false
 	}
 
-	return k.timeProvider.Now().Sub(createdAt) < types.MarketIsRecentDuration
+	// The comparison condition considers both market age and price daemon warmup time because a market can be
+	// created before or after the daemon starts.
+	return k.timeProvider.Now().Sub(createdAt) < types.MarketIsRecentDuration ||
+		ctx.BlockHeight() < types.PriceDaemonInitializationBlocks
 }
 
 // GetAllMarketParamPrices returns a slice of MarketParam, MarketPrice tuples for all markets.
```

### protocol/x/prices/keeper/market_test.go
```diff
@@ -2,6 +2,7 @@ package keeper_test
 
 import (
 	"testing"
+	"time"
 
 	errorsmod "cosmossdk.io/errors"
 	"github.com/dydxprotocol/v4-chain/protocol/daemons/pricefeed/metrics"
@@ -58,22 +59,49 @@ func TestCreateMarket(t *testing.T) {
 	keepertest.AssertMarketCreateEventInIndexerBlock(t, keeper, ctx, marketParam)
 }
 
-func TestMarketIsRecentlyAdded(t *testing.T) {
-	ctx, keeper, _, _, _, mockTimeProvider := keepertest.PricesKeepers(t)
-	mockTimeProvider.On("Now").Return(constants.TimeT).Once()
+func TestMarketIsRecentlyAvailable(t *testing.T) {
+	tests := map[string]struct {
+		blockHeight      int64
+		now              time.Time
+		expectedIsRecent bool
+	}{
+		"Recent: << block height, << elapsed since market creation time": {
+			blockHeight:      0,
+			now:              constants.TimeT.Add(types.MarketIsRecentDuration - 1),
+			expectedIsRecent: true,
+		},
+		"Recent: >> block height, << elapsed since market creation time": {
+			blockHeight:      types.PriceDaemonInitializationBlocks + 1,
+			now:              constants.TimeT.Add(types.MarketIsRecentDuration - 1),
+			expectedIsRecent: true,
+		},
+		"Recent: << block height, >> elapsed since market creation time": {
+			blockHeight:      0,
+			now:              constants.TimeT.Add(types.MarketIsRecentDuration + 1),
+			expectedIsRecent: true,
+		},
+		"Not recent: >> block height, >> elapsed since market creation time": {
+			blockHeight:      types.PriceDaemonInitializationBlocks + 1,
+			now:              constants.TimeT.Add(types.MarketIsRecentDuration + 1),
+			expectedIsRecent: false,
+		},
+	}
+	for name, tc := range tests {
+		t.Run(name, func(t *testing.T) {
+			ctx, keeper, _, _, _, mockTimeProvider := keepertest.PricesKeepers(t)
 
-	// Nonexistent markets should not be recently added.
-	require.False(t, keeper.IsRecentlyAdded(0))
+			// Create market with TimeT creation timestamp.
+			mockTimeProvider.On("Now").Return(constants.TimeT).Once()
+			require.False(t, keeper.IsRecentlyAvailable(ctx, 0))
 
-	keepertest.CreateNMarkets(t, ctx, keeper, 1)
+			keepertest.CreateNMarkets(t, ctx, keeper, 1)
 
-	// Before the duration passes, the market should be recently added.
-	mockTimeProvider.On("Now").Return(constants.TimeT.Add(types.MarketIsRecentDuration - 1)).Once()
-	require.True(t, keeper.IsRecentlyAdded(0))
+			ctx = ctx.WithBlockHeight(tc.blockHeight)
+			mockTimeProvider.On("Now").Return(tc.now).Once()
 
-	// After the duration passes, the market is no longer recently added.
-	mockTimeProvider.On("Now").Return(constants.TimeT.Add(types.MarketIsRecentDuration)).Once()
-	require.False(t, keeper.IsRecentlyAdded(0))
+			require.Equal(t, tc.expectedIsRecent, keeper.IsRecentlyAvailable(ctx, 0))
+		})
+	}
 }
 
 func TestCreateMarket_Errors(t *testing.T) {
```

### protocol/x/prices/keeper/update_price.go
```diff
@@ -66,7 +66,7 @@ func (k Keeper) GetValidMarketPriceUpdates(
 			// Conditionally escalate log level to error 20s after genesis/restart. We expect that it may take a few
 			// seconds for the index price to populate after network genesis or a network restart.
 			logMethod := k.Logger(ctx).Error
-			if k.IsRecentlyAdded(marketId) {
+			if k.IsRecentlyAvailable(ctx, marketId) {
 				logMethod = k.Logger(ctx).Info
 			}
 			logMethod(fmt.Sprintf("Index price for market (%v) does not exist", marketId))
@@ -89,7 +89,7 @@ func (k Keeper) GetValidMarketPriceUpdates(
 			// in populating historical smoothed prices after network genesis or a network restart, because they
 			// depend on present index prices.
 			logMethod := k.Logger(ctx).Error
-			if k.IsRecentlyAdded(marketId) {
+			if k.IsRecentlyAvailable(ctx, marketId) {
 				logMethod = k.Logger(ctx).Info
 			}
 			logMethod(fmt.Sprintf("Smoothed price for market (%v) does not exist", marketId))
```
