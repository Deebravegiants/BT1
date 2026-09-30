# [?] fix: handle race condition in TestAllUpgrades for v4->v5 and v5->v6 (#6575)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-02-16
Source: https://github.com/celestiaorg/celestia-app/commit/370b27dfb56b20bd9ea495ccc3fd385f303c23d9
Type: security-commit

## Details
fix: handle race condition in TestAllUpgrades for v4->v5 and v5->v6 (#6575)

## Summary

- Fix `TestAllUpgrades` subtests `upgrade_from_v4_to_v5` and
`upgrade_from_v5_to_v6` which consistently fail in CI
- The root cause is a race condition: with `TestUpgradeHeightDelay=3`
blocks, the upgrade completes before `GetUpgrade` is queried.
`EndBlocker` applies the upgrade, calls `ResetTally()` (clearing signal
store), and the multiplexer switches binaries (breaking gRPC), so
`GetUpgrade` returns nil.
- `SignalUpgrade` now handles both cases: upgrade still pending (query
`GetUpgrade`) or upgrade already applied (verify via `ABCIInfo` and
compute upgrade height)
- Remove unused `maps.SetField` workaround in `testchain.go`
- Guard `blocksToWait` with `max(..., 2)` to handle already-applied
upgrades

## Test plan

- [x] `TestAllUpgrades` passes all 5 subtests (v2→v3, v3→v4, v4→v5,
v5→v6, v6→v7)
- [x] `TestUpgradeLatest` passes
- [ ] CI passes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### test/docker-e2e/dockerchain/testchain.go
```diff
@@ -12,7 +12,6 @@ import (
 	tastoracontainertypes "github.com/celestiaorg/tastora/framework/docker/container"
 	tastoradockertypes "github.com/celestiaorg/tastora/framework/docker/cosmos"
 	"github.com/celestiaorg/tastora/framework/testutil/config"
-	"github.com/celestiaorg/tastora/framework/testutil/maps"
 	tastoratypes "github.com/celestiaorg/tastora/framework/types"
 	cometcfg "github.com/cometbft/cometbft/config"
 	cmtjson "github.com/cometbft/cometbft/libs/json"
@@ -27,11 +26,6 @@ func NewCelestiaChainBuilder(t *testing.T, cfg *Config) *tastoradockertypes.Chai
 	genesisBz, err := cfg.Genesis.ExportBytes()
 	require.NoError(t, err, "failed to export genesis bytes")
 
-	// TODO: why do I need to do this?
-	// fails with 2025-07-03 14:57:42 Error: failed to get current app state: failed to determine genesis version
-	genesisBz, err = maps.SetField(genesisBz, "consensus.params.version.app", "4")
-	require.NoError(t, err)
-
 	encodingConfig := testutil.MakeTestEncodingConfig(app.ModuleEncodingRegisters...)
 
 	kr := cfg.Genesis.Keyring()
```

### test/docker-e2e/e2e_upgrade_test.go
```diff
@@ -149,8 +149,9 @@ func (s *CelestiaTestSuite) runUpgradeTest(ImageTag string, baseAppVersion, targ
 
 	s.T().Logf("Start height: %d, Upgrade height: %d", startHeight, upgradeHeight)
 
-	// Wait until we reach the upgrade height
-	blocksToWait := int(upgradeHeight-startHeight) + 2 // Add buffer
+	// Wait until we reach the upgrade height. If the upgrade was already
+	// applied (startHeight >= upgradeHeight), just wait for 2 more blocks.
+	blocksToWait := max(int(upgradeHeight-startHeight)+2, 2)
 	s.T().Logf("Waiting for %d blocks to reach upgrade height plus buffer", blocksToWait)
 	s.Require().NoError(wait.ForBlocks(ctx, blocksToWait, chain))
 
@@ -221,7 +222,7 @@ func (s *CelestiaTestSuite) UpgradeChain(ctx context.Context, chain tastoratypes
 	currentHeight, err := s.GetLatestBlockHeight(ctx, rpcClient)
 	s.Require().NoError(err, "failed to get current height")
 
-	blocksToWait := int(upgradeHeight-currentHeight) + 2
+	blocksToWait := max(int(upgradeHeight-currentHeight)+2, 2)
 	t.Logf("Waiting for %d blocks to reach upgrade height %d", blocksToWait, upgradeHeight)
 	s.Require().NoError(wait.ForBlocks(ctx, blocksToWait, chain), "failed to wait for upgrade completion")
 
@@ -282,24 +283,48 @@ func (s *CelestiaTestSuite) SignalUpgrade(
 	s.Require().NoError(err, "failed to broadcast try-upgrade tx")
 	s.Require().Equal(uint32(0), resp.Code, "try-upgrade tx failed with code %d", resp.Code)
 
-	// Wait for one block so that the upgrade transaction is processed
+	tryUpgradeHeight := resp.Height
+	s.T().Logf("MsgTryUpgrade included at height %d", tryUpgradeHeight)
+
+	// Wait for one block so that the upgrade transaction is committed
 	s.Require().NoError(wait.ForBlocks(ctx, 1, chain))
 
-	// Query upgrade info via gRPC
-	s.T().Log("Querying upgrade info via gRPC")
+	// Query upgrade info via gRPC. The upgrade may have already been applied
+	// if the upgrade height delay is small (e.g. 3 blocks for chain-id "test").
+	// In that case, EndBlocker calls ResetTally which clears the upgrade from
+	// the store and the multiplexer switches binaries, breaking the gRPC
+	// connection. We handle both cases:
+	// 1. Upgrade is still pending: GetUpgrade returns the upgrade height.
+	// 2. Upgrade already applied: ABCIInfo shows the target app version.
 	client, cleanup, err := getSignalQueryClient(validatorNode)
 	s.Require().NoError(err)
-	defer cleanup()
 
-	upgradeResp, err := client.GetUpgrade(ctx, &signaltypes.QueryGetUpgradeRequest{})
-	s.Require().NoError(err, "failed to query upgrade info via gRPC")
+	upgradeResp, getUpgradeErr := client.GetUpgrade(ctx, &signaltypes.QueryGetUpgradeRequest{})
+	cleanup()
+
+	if getUpgradeErr == nil && upgradeResp != nil && upgradeResp.Upgrade != nil {
+		upgradeHeight := upgradeResp.Upgrade.UpgradeHeight
+		s.T().Logf("Upgrade pending: app_version=%d height=%d", upgradeResp.Upgrade.AppVersion, upgradeHeight)
+		return upgradeHeight
+	}
+
+	// GetUpgrade didn't return a pending upgrade. Check if the upgrade has
+	// already been applied by querying ABCIInfo via the RPC client.
+	s.T().Log("GetUpgrade returned nil; checking if the upgrade was already applied")
+	rpcClient, err := validatorNode.GetRPCClient()
+	s.Require().NoError(err, "failed to get RPC client")
 
-	// Ensure an upgrade is indeed pending
-	s.Require().NotNil(upgradeResp.Upgrade, "no upgrade pending after try-upgrade")
+	abciInfo, err := rpcClient.ABCIInfo(ctx)
+	s.Require().NoError(err, "failed to query ABCIInfo")
 
-	upgradeHeight := upgradeResp.Upgrade.UpgradeHeight
-	s.T().Logf("Upgrade info: app_version=%d height=%d", upgradeResp.Upgrade.AppVersion, upgradeHeight)
+	currentAppVersion := abciInfo.Response.GetAppVersion()
+	s.Require().Equal(targetAppVersion, currentAppVersion,
+		"upgrade not pending and app version %d does not match target %d", currentAppVersion, targetAppVersion)
 
+	// The upgrade was already applied. Compute the expected upgrade height
+	// from the height at which MsgTryUpgrade was included.
+	upgradeHeight := tryUpgradeHeight + appconsts.GetUpgradeHeightDelay(cfg.Genesis.ChainID)
+	s.T().Logf("Upgrade already applied: app_version=%d, computed upgrade height=%d", currentAppVersion, upgradeHeight)
 	return upgradeHeight
 }
 
```
