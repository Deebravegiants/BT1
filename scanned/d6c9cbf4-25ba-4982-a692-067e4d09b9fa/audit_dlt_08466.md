# [?] 9.5 upgrade & add underflow protection for referred volume (#3261)

## Summary
Severity: Unknown
Chain: dYdX
Component: dydxprotocol/v4-chain
Published: 2025-12-02
Source: https://github.com/dydxprotocol/v4-chain/commit/4c4f705897c895148026eca0ce0249f41b36d85d
Type: security-commit

## Details
9.5 upgrade & add underflow protection for referred volume (#3261)

## Patch
### protocol/app/upgrades.go
```diff
@@ -3,7 +3,7 @@ package app
 import (
 	"fmt"
 
-	v_9_4 "github.com/dydxprotocol/v4-chain/protocol/app/upgrades/v9.4"
+	v_9_5 "github.com/dydxprotocol/v4-chain/protocol/app/upgrades/v9.5"
 
 	upgradetypes "cosmossdk.io/x/upgrade/types"
 	sdk "github.com/cosmos/cosmos-sdk/types"
@@ -14,23 +14,24 @@ var (
 	// `Upgrades` defines the upgrade handlers and store loaders for the application.
 	// New upgrades should be added to this slice after they are implemented.
 	Upgrades = []upgrades.Upgrade{
-		v_9_4.Upgrade,
+		v_9_5.Upgrade,
 	}
 	Forks = []upgrades.Fork{}
 )
 
 // setupUpgradeHandlers registers the upgrade handlers to perform custom upgrade
 // logic and state migrations for software upgrades.
 func (app *App) setupUpgradeHandlers() {
-	if app.UpgradeKeeper.HasHandler(v_9_4.UpgradeName) {
-		panic(fmt.Sprintf("Cannot register duplicate upgrade handler '%s'", v_9_4.UpgradeName))
+	if app.UpgradeKeeper.HasHandler(v_9_5.UpgradeName) {
+		panic(fmt.Sprintf("Cannot register duplicate upgrade handler '%s'", v_9_5.UpgradeName))
 	}
 	app.UpgradeKeeper.SetUpgradeHandler(
-		v_9_4.UpgradeName,
-		v_9_4.CreateUpgradeHandler(
+		v_9_5.UpgradeName,
+		v_9_5.CreateUpgradeHandler(
 			app.ModuleManager,
-			app.AffiliatesKeeper,
 			app.configurator,
+			app.StatsKeeper,
+			app.EpochsKeeper,
 		),
 	)
 }
```

### protocol/app/upgrades/v9.4/upgrade_container_test.go
```diff
@@ -1,89 +0,0 @@
-//go:build all || container_test
-
-package v_9_4_test
-
-import (
-	"testing"
-
-	"github.com/cosmos/gogoproto/proto"
-	v_9_4 "github.com/dydxprotocol/v4-chain/protocol/app/upgrades/v9.4"
-	"github.com/dydxprotocol/v4-chain/protocol/testing/containertest"
-	"github.com/dydxprotocol/v4-chain/protocol/testutil/constants"
-	affiliatetypes "github.com/dydxprotocol/v4-chain/protocol/x/affiliates/types"
-	"github.com/stretchr/testify/require"
-)
-
-func TestStateUpgrade(t *testing.T) {
-	testnet, err := containertest.NewTestnetWithPreupgradeGenesis()
-	require.NoError(t, err, "failed to create testnet - is docker daemon running?")
-	err = testnet.Start()
-	require.NoError(t, err)
-	defer testnet.MustCleanUp()
-	node := testnet.Nodes["alice"]
-	nodeAddress := constants.AliceAccAddress.String()
-
-	preUpgradeSetups(node, t)
-	preUpgradeChecks(node, t)
-
-	err = containertest.UpgradeTestnet(nodeAddress, t, node, v_9_4.UpgradeName)
-	require.NoError(t, err)
-
-	postUpgradeChecks(node, t)
-}
-
-func preUpgradeSetups(node *containertest.Node, t *testing.T) {}
-
-func preUpgradeChecks(node *containertest.Node, t *testing.T) {
-	// Verify affiliate tiers are set to default values
-	tiersResp := &affiliatetypes.AllAffiliateTiersResponse{}
-	resp, err := containertest.Query(
-		node,
-		affiliatetypes.NewQueryClient,
-		affiliatetypes.QueryClient.AllAffiliateTiers,
-		&affiliatetypes.AllAffiliateTiersRequest{},
-	)
-	require.NoError(t, err)
-	err = proto.UnmarshalText(resp.String(), tiersResp)
-	require.NoError(t, err)
-	require.Equal(t, v_9_4.PreviousAffilliateTiers, tiersResp.Tiers)
-}
-
-func postUpgradeChecks(node *containertest.Node, t *testing.T) {
-	// Verify affiliate tiers are set to default values
-	tiersResp := &affiliatetypes.AllAffiliateTiersResponse{}
-	resp, err := containertest.Query(
-		node,
-		affiliatetypes.NewQueryClient,
-		affiliatetypes.QueryClient.AllAffiliateTiers,
-		&affiliatetypes.AllAffiliateTiersRequest{},
-	)
-	require.NoError(t, err)
-	err = proto.UnmarshalText(resp.String(), tiersResp)
-	require.NoError(t, err)
-	require.Equal(t, v_9_4.UpdatedAffiliateTiers, tiersResp.Tiers)
-
-	// Verify affiliate parameters are set to default values
-	paramsResp := &affiliatetypes.AffiliateParametersResponse{}
-	resp, err = containertest.Query(
-		node,
-		affiliatetypes.NewQueryClient,
-		affiliatetypes.QueryClient.AffiliateParameters,
-		&affiliatetypes.AffiliateParametersRequest{},
-	)
-	require.NoError(t, err)
-	err = proto.UnmarshalText(resp.String(), paramsResp)
-	require.NoError(t, err)
-	require.Equal(t, v_9_4.UpdatedAffiliateParameters, paramsResp.Parameters)
-
-	// Verify affiliate overrides were migrated from whitelist
-	overridesResp := &affiliatetypes.AffiliateOverridesResponse{}
-	resp, err = containertest.Query(
-		node,
-		affiliatetypes.NewQueryClient,
-		affiliatetypes.QueryClient.AffiliateOverrides,
-		&affiliatetypes.AffiliateOverridesRequest{},
-	)
-	require.NoError(t, err)
-	err = proto.UnmarshalText(resp.String(), overridesResp)
-	require.NoError(t, err)
-}
```

### protocol/app/upgrades/v9.5/constants.go
```diff
@@ -0,0 +1,15 @@
+package v_9_5
+
+import (
+	store "cosmossdk.io/store/types"
+	"github.com/dydxprotocol/v4-chain/protocol/app/upgrades"
+)
+
+const (
+	UpgradeName = "v9.5"
+)
+
+var Upgrade = upgrades.Upgrade{
+	UpgradeName:   UpgradeName,
+	StoreUpgrades: store.StoreUpgrades{},
+}
```

### protocol/app/upgrades/v9.5/upgrade.go
```diff
@@ -0,0 +1,127 @@
+package v_9_5
+
+import (
+	"context"
+	"fmt"
+	"sort"
+
+	upgradetypes "cosmossdk.io/x/upgrade/types"
+	sdk "github.com/cosmos/cosmos-sdk/types"
+	"github.com/cosmos/cosmos-sdk/types/module"
+
+	"github.com/dydxprotocol/v4-chain/protocol/lib"
+	epochskeeper "github.com/dydxprotocol/v4-chain/protocol/x/epochs/keeper"
+	statskeeper "github.com/dydxprotocol/v4-chain/protocol/x/stats/keeper"
+	statstypes "github.com/dydxprotocol/v4-chain/protocol/x/stats/types"
+)
+
+// Migrate30dReferredVolumeToEpochStats migrates all users' 30d referred volume
+// to epoch stats in the current epoch.
+func Migrate30dReferredVolumeToEpochStats(
+	ctx sdk.Context,
+	statsKeeper statskeeper.Keeper,
+	epochsKeeper epochskeeper.Keeper,
+) {
+	// Get the current stats epoch
+	statsEpochInfo := epochsKeeper.MustGetStatsEpochInfo(ctx)
+	currentEpoch := statsEpochInfo.CurrentEpoch
+
+	ctx.Logger().Info(fmt.Sprintf(
+		"Migrating 30d referred volume to epoch stats for epoch %d",
+		currentEpoch,
+	))
+
+	// Get or create epoch stats for current epoch
+	epochStats := statsKeeper.GetEpochStatsOrNil(ctx, currentEpoch)
+	if epochStats == nil {
+		epochStats = &statstypes.EpochStats{
+			Stats: []*statstypes.EpochStats_UserWithStats{},
+		}
+	}
+
+	// Create a map for existing epoch stats for quick lookup
+	userStatsMap := make(map[string]*statstypes.EpochStats_UserWithStats)
+	for _, userWithStats := range epochStats.Stats {
+		userStatsMap[userWithStats.User] = userWithStats
+	}
+
+	// Get all addresses with referred volume from the global UserStats
+	allAddressesWithReferredVolume := statsKeeper.GetAllAddressesWithReferredVolume(ctx)
+
+	migratedCount := 0
+
+	for _, address := range allAddressesWithReferredVolume {
+		// Get the global user stats which contains the 30d referred volume
+		globalUserStats := statsKeeper.GetUserStats(ctx, address)
+		if globalUserStats == nil {
+			continue
+		}
+
+		referredVolume := globalUserStats.Affiliate_30DReferredVolumeQuoteQuantums
+
+		// Get or create user stats for this epoch
+		epochUserStats, exists := userStatsMap[address]
+		if !exists {
+			// User not in epoch stats yet, create new entry
+			epochUserStats = &statstypes.EpochStats_UserWithStats{
+				User: address,
+				Stats: &statstypes.UserStats{
+					Affiliate_30DReferredVolumeQuoteQuantums: referredVolume,
+				},
+			}
+			userStatsMap[address] = epochUserStats
+		} else {
+			// User already in epoch stats, add the referred volume
+			epochUserStats.Stats.Affiliate_30DReferredVolumeQuoteQuantums += referredVolume
+		}
+
+		migratedCount++
+
+		ctx.Logger().Info(fmt.Sprintf(
+			"Migrated referred volume for address %s (%d of %d): Affiliate_30DReferredVolumeQuoteQuantums=%d",
+			address,
+			migratedCount,
+			len(allAddressesWithReferredVolume),
+			referredVolume,
+		))
+	}
+
+	// Convert map back to slice - must be deterministic to avoid state hash mismatch
+	keys := make([]string, 0, len(userStatsMap))
+	for k := range userStatsMap {
+		keys = append(keys, k)
+	}
+	sort.Strings(keys)
+	epochStats.Stats = make([]*statstypes.EpochStats_UserWithStats, 0, len(userStatsMap))
+	for _, k := range keys {
+		epochStats.Stats = append(epochStats.Stats, userStatsMap[k])
+	}
+
+	// Save the updated epoch stats
+	statsKeeper.SetEpochStats(ctx, currentEpoch, epochStats)
+
+	ctx.Logger().Info(fmt.Sprintf(
+		"Successfully migrated 30d referred volume for %d addresses to epoch %d",
+		migratedCount,
+		currentEpoch,
+	))
+}
+
+func CreateUpgradeHandler(
+	mm *module.Manager,
+	configurator module.Configurator,
+	statsKeeper statskeeper.Keeper,
+	epochsKeeper epochskeeper.Keeper,
+) upgradetypes.UpgradeHandler {
+	return func(ctx context.Context, plan upgradetypes.Plan, vm module.VersionMap) (module.VersionMap, error) {
+		sdkCtx := lib.UnwrapSDKContext(ctx, "app/upgrades")
+		sdkCtx.Logger().Info(fmt.Sprintf("Running %s Upgrade...", UpgradeName))
+
+		// Migrate 30d referred volume to epoch stats
+		Migrate30dReferredVolumeToEpochStats(sdkCtx, statsKeeper, epochsKeeper)
+
+		sdkCtx.Logger().Info(fmt.Sprintf("Successfully completed %s Upgrade", UpgradeName))
+
+		return mm.RunMigrations(ctx, configurator, vm)
+	}
+}
```

### protocol/app/upgrades/v9.5/upgrade_container_test.go
```diff
@@ -0,0 +1,200 @@
+package v_9_5_test
+
+import (
+	"testing"
+
+	"github.com/stretchr/testify/require"
+
+	v_9_5 "github.com/dydxprotocol/v4-chain/protocol/app/upgrades/v9.5"
+	"github.com/dydxprotocol/v4-chain/protocol/testing/containertest"
+	testapp "github.com/dydxprotocol/v4-chain/protocol/testutil/app"
+	"github.com/dydxprotocol/v4-chain/protocol/testutil/constants"
+	statstypes "github.com/dydxprotocol/v4-chain/protocol/x/stats/types"
+)
+
+func TestMigrate30dReferredVolumeToEpochStats(t *testing.T) {
+	tApp := testapp.NewTestAppBuilder(t).Build()
+	tApp.InitChain()
+
+	statsKeeper := tApp.App.StatsKeeper
+	epochsKeeper := tApp.App.EpochsKeeper
+
+	// Advance to the next epoch so we have a current epoch with some activity
+	ctx := tApp.AdvanceToBlock(10, testapp.AdvanceToBlockOptions{})
+
+	// Query epochs info to get current epoch
+	statsEpochInfo := epochsKeeper.MustGetStatsEpochInfo(ctx)
+	currentEpoch := statsEpochInfo.CurrentEpoch
+
+	// Create some initial epoch stats (simulating existing trading activity)
+	initialEpochStats := &statstypes.EpochStats{
+		Stats: []*statstypes.EpochStats_UserWithStats{
+			{
+				User: constants.AliceAccAddress.String(),
+				Stats: &statstypes.UserStats{
+					TakerNotional: 50,
+					MakerNotional: 75,
+					// No referred volume set yet
+				},
+			},
+			{
+				User: constants.BobAccAddress.String(),
+				Stats: &statstypes.UserStats{
+					TakerNotional: 100,
+					MakerNotional: 150,
+					// No referred volume set yet
+				},
+			},
+		},
+	}
+	statsKeeper.SetEpochStats(ctx, currentEpoch, initialEpochStats)
+
+	// Set up global user stats with referred volume (this represents the 30d cumulative volume)
+	testUsers := []struct {
+		address        string
+		referredVolume uint64
+	}{
+		{constants.AliceAccAddress.String(), 1_000_000_000}, // 1k volume
+		{constants.BobAccAddress.String(), 5_000_000_000},   // 5k volume
+		{constants.CarlAccAddress.String(), 10_000_000_000}, // 10k volume
+		{constants.DaveAccAddress.String(), 0},              // no referred volume
+	}
+
+	for _, user := range testUsers {
+		userStats := &statstypes.UserStats{
+			TakerNotional:                            100,
+			MakerNotional:                            200,
+			Affiliate_30DReferredVolumeQuoteQuantums: user.referredVolume,
+		}
+		statsKeeper.SetUserStats(ctx, user.address, userStats)
+	}
+
+	// Verify initial state - epoch stats should not have referred volume
+	preUpgradeEpochStats := statsKeeper.GetEpochStatsOrNil(ctx, currentEpoch)
+	require.NotNil(t, preUpgradeEpochStats)
+	for _, userStats := range preUpgradeEpochStats.Stats {
+		require.Equal(t, uint64(0), userStats.Stats.Affiliate_30DReferredVolumeQuoteQuantums,
+			"Referred volume should be 0 before migration for user %s", userStats.User)
+	}
+
+	// Run the migration function directly
+	v_9_5.Migrate30dReferredVolumeToEpochStats(ctx, statsKeeper, epochsKeeper)
+
+	// Verify migration results
+	postUpgradeEpochStats := statsKeeper.GetEpochStatsOrNil(ctx, currentEpoch)
+	require.NotNil(t, postUpgradeEpochStats)
+
+	// Create a map for easier verification
+	epochStatsMap := make(map[string]*statstypes.EpochStats_UserWithStats)
+	for _, userStats := range postUpgradeEpochStats.Stats {
+		epochStatsMap[userStats.User] = userStats
+	}
+
+	// Verify Alice's referred volume was migrated
+	aliceStats, exists := epochStatsMap[constants.AliceAccAddress.String()]
+	require.True(t, exists, "Alice should exist in epoch stats")
+	require.Equal(t, uint64(1_000_000_000), aliceStats.Stats.Affiliate_30DReferredVolumeQuoteQuantums,
+		"Alice's referred volume should be migrated")
+	require.Equal(t, uint64(50), aliceStats.Stats.TakerNotional,
+		"Alice's taker notional should be preserved")
+	require.Equal(t, uint64(75), aliceStats.Stats.MakerNotional,
+		"Alice's maker notional should be preserved")
+
+	// Verify Bob's referred volume was migrated
+	bobStats, exists := epochStatsMap[constants.BobAccAddress.String()]
+	require.True(t, exists, "Bob should exist in epoch stats")
+	require.Equal(t, uint64(5_000_000_000), bobStats.Stats.Affiliate_30DReferredVolumeQuoteQuantums,
+		"Bob's referred volume should be migrated")
+	require.Equal(t, uint64(100), bobStats.Stats.TakerNotional,
+		"Bob's taker notional should be preserved")
+	require.Equal(t, uint64(150), bobStats.Stats.MakerNotional,
+		"Bob's maker notional should be preserved")
+
+	// Verify Carl is NOW in epoch stats (even though he wasn't trading, he has referred volume)
+	carlStats, carlExists := epochStatsMap[constants.CarlAccAddress.String()]
+	require.True(t, carlExists, "Carl should be in epoch stats because he has referred volume")
+	require.Equal(t, uint64(10_000_000_000), carlStats.Stats.Affiliate_30DReferredVolumeQuoteQuantums,
+		"Carl's referred volume should be migrated")
+	require.Equal(t, uint64(0), carlStats.Stats.TakerNotional,
+		"Carl's taker notional should be 0 (he wasn't trading)")
+	require.Equal(t, uint64(0), carlStats.Stats.MakerNotional,
+		"Carl's maker notional should be 0 (he wasn't trading)")
+
+	// Verify Dave is NOT in epoch stats (he has no referred volume)
+	_, daveExists := epochStatsMap[constants.DaveAccAddress.String()]
+	require.False(t, daveExists, "Dave should not be in epoch stats as he has no referred volume")
+}
+
+func TestMigrate30dReferredVolumeToEpochStats_EmptyEpochStats(t *testing.T) {
+	tApp := testapp.NewTestAppBuilder(t).Build()
+	tApp.InitChain()
+
+	statsKeeper := tApp.App.StatsKeeper
+	epochsKeeper := tApp.App.EpochsKeeper
+
+	// Advance to next epoch
+	ctx := tApp.AdvanceToBlock(10, testapp.AdvanceToBlockOptions{})
+
+	// Query epochs info to get current epoch
+	statsEpochInfo := epochsKeeper.MustGetStatsEpochInfo(ctx)
+	currentEpoch := statsEpochInfo.CurrentEpoch
+
+	// Setup: Create user stats with referred volume but no epoch stats
+	userStats := &statstypes.UserStats{
+		TakerNotional:                            100,
+		MakerNotional:                            200,
+		Affiliate_30DReferredVolumeQuoteQuantums: 1_000_000_000,
+	}
+	statsKeeper.SetUserStats(ctx, constants.AliceAccAddress.String(), userStats)
+
+	// Verify no epoch stats exist initially
+	preUpgradeEpochStats := statsKeeper.GetEpochStatsOrNil(ctx, currentEpoch)
+	require.Nil(t, preUpgradeEpochStats)
+
+	// Run the migration function directly
+	v_9_5.Migrate30dReferredVolumeToEpochStats(ctx, statsKeeper, epochsKeeper)
+
+	// Verify Alice was added to epoch stats even though she wasn't trading
+	postUpgradeEpochStats := statsKeeper.GetEpochStatsOrNil(ctx, currentEpoch)
+	require.NotNil(t, postUpgradeEpochStats)
+	require.Len(t, postUpgradeEpochStats.Stats, 1,
+		"Alice should be added to epoch stats because she has referred volume")
+
+	aliceStats := postUpgradeEpochStats.Stats[0]
+	require.Equal(t, constants.AliceAccAddress.String(), aliceStats.User)
+	require.Equal(t, uint64(1_000_000_000), aliceStats.Stats.Affiliate_30DReferredVolumeQuoteQuantums,
+		"Alice's referred volume should be migrated")
+	require.Equal(t, uint64(0), aliceStats.Stats.TakerNotional,
+		"Alice's taker notional should be 0 (she wasn't trading)")
+	require.Equal(t, uint64(0), aliceStats.Stats.MakerNotional,
+		"Alice's maker notional should be 0 (she wasn't trading)")
+}
+
+func TestStateUpgrade(t *testing.T) {
+	testnet, err := containertest.NewTestnetWithPreupgradeGenesis()
+	require.NoError(t, err, "failed to create testnet - is docker daemon running?")
+	err = testnet.Start()
+	require.NoError(t, err)
+	defer testnet.MustCleanUp()
+	node := testnet.Nodes["alice"]
+	nodeAddress := constants.AliceAccAddress.String()
+
+	preUpgradeSetups(node, t)
+	preUpgradeChecks(node, t)
+
+	err = containertest.UpgradeTestnet(nodeAddress, t, node, v_9_5.UpgradeName)
+	require.NoError(t, err)
+
+	postUpgradeChecks(node, t)
+}
+
+func preUpgradeSetups(node *containertest.Node, t *testing.T) {
+	// Set up user stats with referred volume before upgrade
+	// This simulates users having 30d referred volume in global stats
+}
+
+func preUpgradeChecks(node *containertest.Node, t *testing.T) {
+}
+
+func postUpgradeChecks(node *containertest.Node, t *testing.T) {
+}
```

### protocol/testing/version/VERSION_CURRENT
```diff
@@ -1 +1 @@
-v9.4
\ No newline at end of file
+v9.5
\ No newline at end of file
```

### protocol/testing/version/VERSION_FULL_NAME_PREUPGRADE
```diff
@@ -1 +1 @@
-v9.3.0
\ No newline at end of file
+v9.4.0
\ No newline at end of file
```

### protocol/testing/version/VERSION_PREUPGRADE
```diff
@@ -1 +1 @@
-v9.3
\ No newline at end of file
+v9.4
\ No newline at end of file
```

### protocol/x/stats/keeper/keeper.go
```diff
@@ -331,9 +331,26 @@ func (k Keeper) ExpireOldStats(ctx sdk.Context) {
 		stats := k.GetUserStats(ctx, removedStats.User)
 		stats.TakerNotional -= removedStats.Stats.TakerNotional
 		stats.MakerNotional -= removedStats.Stats.MakerNotional
-		stats.Affiliate_30DRevenueGeneratedQuantums -= removedStats.Stats.Affiliate_30DRevenueGeneratedQuantums
-		stats.Affiliate_30DReferredVolumeQuoteQuantums -= removedStats.Stats.Affiliate_30DReferredVolumeQuoteQuantums
-		stats.Affiliate_30DAttributedVolumeQuoteQuantums -= removedStats.Stats.Affiliate_30DAttributedVolumeQuoteQuantums
+		// Clamp affiliate_30drevenue at 0 to prevent underflow (must compare before subtracting for uint64)
+		if stats.Affiliate_30DRevenueGeneratedQuantums > removedStats.Stats.Affiliate_30DRevenueGeneratedQuantums {
+			stats.Affiliate_30DRevenueGeneratedQuantums -= removedStats.Stats.Affiliate_30DRevenueGeneratedQuantums
+		} else {
+			stats.Affiliate_30DRevenueGeneratedQuantums = 0
+		}
+
+		// Clamp affiliate fields at 0 to prevent underflow (must compare before subtracting for uint64)
+		if stats.Affiliate_30DReferredVolumeQuoteQuantums > removedStats.Stats.Affiliate_30DReferredVolumeQuoteQuantums {
+			stats.Affiliate_30DReferredVolumeQuoteQuantums -= removedStats.Stats.Affiliate_30DReferredVolumeQuoteQuantums
+		} else {
+			stats.Affiliate_30DReferredVolumeQuoteQuantums = 0
+		}
+
+		if stats.Affiliate_30DAttributedVolumeQuoteQuantums > removedStats.Stats.Affiliate_30DAttributedVolumeQuoteQuantums {
+			stats.Affiliate_30DAttributedVolumeQuoteQuantums -= removedStats.Stats.Affiliate_30DAttributedVolumeQuoteQuantums
+		} else {
+			stats.Affiliate_30DAttributedVolumeQuoteQuantums = 0
+		}
+
 		k.SetUserStats(ctx, removedStats.User, stats)
 
 		// Just remove TakerNotional to avoid double counting
@@ -439,3 +456,23 @@ func (k Keeper) UnsafeSetCachedStakedBaseTokens(ctx sdk.Context, delegatorAddr s
 	store := prefix.NewStore(ctx.KVStore(k.storeKey), []byte(types.CachedStakeAmountKeyPrefix))
 	store.Set([]byte(delegatorAddr), k.cdc.MustMarshal(cachedStakedBaseTokens))
 }
+
+// GetAllAddressesWithReferredVolume returns all addresses that have non-zero referred volume.
+// This is useful for migrations.
+func (k Keeper) GetAllAddressesWithReferredVolume(ctx sdk.Context) []string {
+	store := prefix.NewStore(ctx.KVStore(k.storeKey), []byte(types.UserStatsKeyPrefix))
+	iterator := store.Iterator(nil, nil)
+	defer iterator.Close()
+
+	addresses := make([]string, 0)
+	for ; iterator.Valid(); iterator.Next() {
+		var userStats types.UserStats
+		k.cdc.MustUnmarshal(iterator.Value(), &userStats)
+
+		if userStats.Affiliate_30DReferredVolumeQuoteQuantums > 0 {
+			addresses = append(addresses, string(iterator.Key()))
+		}
+	}
+
+	return addresses
+}
```

### protocol/x/stats/keeper/keeper_test.go
```diff
@@ -994,3 +994,228 @@ func TestGetStakedBaseTokens_Cache_Miss(t *testing.T) {
 	receivedCoins := statsKeeper.GetStakedBaseTokens(ctx, constants.AliceAccAddress.String())
 	require.Equal(t, latestCoinsToStakeQuantums, receivedCoins)
 }
+
+// TestExpireOldStats_UnderflowProtection tests that affiliate fields are properly
+// clamped to 0 when expiring epochs would cause underflow due to corrupted/inconsistent data.
+func TestExpireOldStats_UnderflowProtection(t *testing.T) {
+	tApp := testapp.NewTestAppBuilder(t).Build()
+
+	// Epochs start at block height 2
+	ctx := tApp.AdvanceToBlock(2, testapp.AdvanceToBlockOptions{
+		BlockTime: time.Unix(int64(1), 0).UTC(),
+	})
+	windowDuration := tApp.App.StatsKeeper.GetWindowDuration(ctx)
+
+	// Advance time so epochs can expire
+	tApp.AdvanceToBlock(3, testapp.AdvanceToBlockOptions{
+		BlockTime: time.Unix(0, 0).
+			Add(windowDuration).
+			Add((time.Duration(2*epochstypes.StatsEpochDuration) + 1) * time.Second).
+			UTC(),
+	})
+	ctx = tApp.AdvanceToBlock(100, testapp.AdvanceToBlockOptions{})
+	k := tApp.App.StatsKeeper
+
+	// Simulate a scenario where epoch stats have MORE volume than user's current stats
+	// This could happen after the v9.5 migration or other data inconsistencies
+
+	// Create epoch 0 with large affiliate volumes
+	k.SetEpochStats(ctx, 0, &types.EpochStats{
+		EpochEndTime: time.Unix(0, 0).UTC(),
+		Stats: []*types.EpochStats_UserWithStats{
+			{
+				User: "alice",
+				Stats: &types.UserStats{
+					TakerNotional:                              100,
+					MakerNotional:                              200,
+					Affiliate_30DReferredVolumeQuoteQuantums:   1_000_000_000_000, // 1M volume in epoch
+					Affiliate_30DAttributedVolumeQuoteQuantums: 500_000_000_000,   // 500k attributed
+				},
+			},
+		},
+	})
+
+	// Set user stats with LESS than what's in the epoch
+	// This simulates corrupted/inconsistent state
+	k.SetUserStats(ctx, "alice", &types.UserStats{
+		TakerNotional:                              50,              // Less than epoch
+		MakerNotional:                              100,             // Less than epoch
+		Affiliate_30DReferredVolumeQuoteQuantums:   100_000_000_000, // Only 100k, but epoch has 1M
+		Affiliate_30DAttributedVolumeQuoteQuantums: 50_000_000_000,  // Only 50k, but epoch has 500k
+	})
+
+	k.SetGlobalStats(ctx, &types.GlobalStats{
+		NotionalTraded: 150,
+	})
+
+	k.SetStatsMetadata(ctx, &types.StatsMetadata{
+		TrailingEpoch: 0,
+	})
+
+	// Expire the epoch - this should NOT cause underflow
+	k.ExpireOldStats(ctx)
+
+	// Verify that affiliate fields are clamped to 0, not wrapped around to huge numbers
+	aliceStats := k.GetUserStats(ctx, "alice")
+
+	// TakerNotional and MakerNotional can go negative (they wrap around for uint64)
+	// But we're testing that the affiliate fields with underflow protection work correctly
+
+	// These fields should be clamped to 0, not underflow
+	require.Equal(t, uint64(0), aliceStats.Affiliate_30DReferredVolumeQuoteQuantums,
+		"Referred volume should be clamped to 0, not underflow")
+	require.Equal(t, uint64(0), aliceStats.Affiliate_30DAttributedVolumeQuoteQuantums,
+		"Attributed volume should be clamped to 0, not underflow")
+
+	// Verify the values aren't huge wrapped-around numbers
+	// If underflow occurred, these would be close to uint64 max (18446744073709551615)
+	require.Less(t, aliceStats.Affiliate_30DReferredVolumeQuoteQuantums, uint64(1000),
+		"Referred volume should not be a wrapped-around huge number")
+	require.Less(t, aliceStats.Affiliate_30DAttributedVolumeQuoteQuantums, uint64(1000),
+		"Attributed volume should not be a wrapped-around huge number")
+}
+
+// TestExpireOldStats_UnderflowProtection_EdgeCase tests the exact boundary case
+func TestExpireOldStats_UnderflowProtection_EdgeCase(t *testing.T) {
+	tApp := testapp.NewTestAppBuilder(t).Build()
+
+	ctx := tApp.AdvanceToBlock(2, testapp.AdvanceToBlockOptions{
+		BlockTime: time.Unix(int64(1), 0).UTC(),
+	})
+	windowDuration := tApp.App.StatsKeeper.GetWindowDuration(ctx)
+
+	tApp.AdvanceToBlock(3, testapp.AdvanceToBlockOptions{
+		BlockTime: time.Unix(0, 0).
+			Add(windowDuration).
+			Add((time.Duration(2*epochstypes.StatsEpochDuration) + 1) * time.Second).
+			UTC(),
+	})
+	ctx = tApp.AdvanceToBlock(100, testapp.AdvanceToBlockOptions{})
+	k := tApp.App.StatsKeeper
+
+	// Test exact boundary: user has exactly the same amount as epoch
+	k.SetEpochStats(ctx, 0, &types.EpochStats{
+		EpochEndTime: time.Unix(0, 0).UTC(),
+		Stats: []*types.EpochStats_UserWithStats{
+			{
+				User: "bob",
+				Stats: &types.UserStats{
+					Affiliate_30DReferredVolumeQuoteQuantums:   1000,
+					Affiliate_30DAttributedVolumeQuoteQuantums: 500,
+				},
+			},
+		},
+	})
+
+	k.SetUserStats(ctx, "bob", &types.UserStats{
+		Affiliate_30DReferredVolumeQuoteQuantums:   1000, // Exactly the same
+		Affiliate_30DAttributedVolumeQuoteQuantums: 500,  // Exactly the same
+	})
+
+	k.SetStatsMetadata(ctx, &types.StatsMetadata{
+		TrailingEpoch: 0,
+	})
+
+	k.ExpireOldStats(ctx)
+
+	bobStats := k.GetUserStats(ctx, "bob")
+
+	// Should be exactly 0 after subtracting equal amounts
+	require.Equal(t, uint64(0), bobStats.Affiliate_30DReferredVolumeQuoteQuantums,
+		"Should be exactly 0 after subtracting equal amounts")
+	require.Equal(t, uint64(0), bobStats.Affiliate_30DAttributedVolumeQuoteQuantums,
+		"Should be exactly 0 after subtracting equal amounts")
+}
+
+// TestExpireOldStats_UnderflowProtection_MultipleUsers tests that underflow
+// protection works correctly when multiple users have inconsistent data
+func TestExpireOldStats_UnderflowProtection_MultipleUsers(t *testing.T) {
+	tApp := testapp.NewTestAppBuilder(t).Build()
+
+	ctx := tApp.AdvanceToBlock(2, testapp.AdvanceToBlockOptions{
+		BlockTime: time.Unix(int64(1), 0).UTC(),
+	})
+	windowDuration := tApp.App.StatsKeeper.GetWindowDuration(ctx)
+
+	tApp.AdvanceToBlock(3, testapp.AdvanceToBlockOptions{
+		BlockTime: time.Unix(0, 0).
+			Add(windowDuration).
+			Add((time.Duration(2*epochstypes.StatsEpochDuration) + 1) * time.Second).
+			UTC(),
+	})
+	ctx = tApp.AdvanceToBlock(100, testapp.AdvanceToBlockOptions{})
+	k := tApp.App.StatsKeeper
+
+	// Create epoch with multiple users having different underflow scenarios
+	k.SetEpochStats(ctx, 0, &types.EpochStats{
+		EpochEndTime: time.Unix(0, 0).UTC(),
+		Stats: []*types.EpochStats_UserWithStats{
+			{
+				User: "alice",
+				Stats: &types.UserStats{
+					Affiliate_30DReferredVolumeQuoteQuantums:   5_000_000_000,
+					Affiliate_30DAttributedVolumeQuoteQuantums: 3_000_000_000,
+				},
+			},
+			{
+				User: "bob",
+				Stats: &types.UserStats{
+					Affiliate_30DReferredVolumeQuoteQuantums:   10_000_000_000,
+					Affiliate_30DAttributedVolumeQuoteQuantums: 7_000_000_000,
+				},
+			},
+			{
+				User: "carl",
+				Stats: &types.UserStats{
+					Affiliate_30DReferredVolumeQuoteQuantums:   2_000_000_000,
+					Affiliate_30DAttributedVolumeQuoteQuantums: 1_000_000_000,
+				},
+			},
+		},
+	})
+
+	// Alice: has more than epoch (normal case)
+	k.SetUserStats(ctx, "alice", &types.UserStats{
+		Affiliate_30DReferredVolumeQuoteQuantums:   10_000_000_000,
+		Affiliate_30DAttributedVolumeQuoteQuantums: 8_000_000_000,
+	})
+
+	// Bob: has less than epoch (should clamp to 0)
+	k.SetUserStats(ctx, "bob", &types.UserStats{
+		Affiliate_30DReferredVolumeQuoteQuantums:   5_000_000_000,
+		Affiliate_30DAttributedVolumeQuoteQuantums: 3_000_000_000,
+	})
+
+	// Carl: has exactly the same (should become 0)
+	k.SetUserStats(ctx, "carl", &types.UserStats{
+		Affiliate_30DReferredVolumeQuoteQuantums:   2_000_000_000,
+		Affiliate_30DAttributedVolumeQuoteQuantums: 1_000_000_000,
+	})
+
+	k.SetStatsMetadata(ctx, &types.StatsMetadata{
+		TrailingEpoch: 0,
+	})
+
+	k.ExpireOldStats(ctx)
+
+	// Verify Alice: normal subtraction
+	aliceStats := k.GetUserStats(ctx, "alice")
+	require.Equal(t, uint64(5_000_000_000), aliceStats.Affiliate_30DReferredVolumeQuoteQuantums,
+		"Alice should have 5B remaining (10B - 5B)")
+	require.Equal(t, uint64(5_000_000_000), aliceStats.Affiliate_30DAttributedVolumeQuoteQuantums,
+		"Alice should have 5B remaining (8B - 3B)")
+
+	// Verify Bob: clamped to 0
+	bobStats := k.GetUserStats(ctx, "bob")
+	require.Equal(t, uint64(0), bobStats.Affiliate_30DReferredVolumeQuoteQuantums,
+		"Bob should be clamped to 0 (had 5B, tried to subtract 10B)")
+	require.Equal(t, uint64(0), bobStats.Affiliate_30DAttributedVolumeQuoteQuantums,
+		"Bob should be clamped to 0 (had 3B, tried to subtract 7B)")
+
+	// Verify Carl: exactly 0
+	carlStats := k.GetUserStats(ctx, "carl")
+	require.Equal(t, uint64(0), carlStats.Affiliate_30DReferredVolumeQuoteQuantums,
+		"Carl should be exactly 0 (had 2B, subtracted 2B)")
+	require.Equal(t, uint64(0), carlStats.Affiliate_30DAttributedVolumeQuoteQuantums,
+		"Carl should be exactly 0 (had 1B, subtracted 1B)")
+}
```
