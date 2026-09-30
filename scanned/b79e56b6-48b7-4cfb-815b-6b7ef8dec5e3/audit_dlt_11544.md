# [?] Fix overflow on node block stale measure & store duration blocks override values when test-mode is enabled (#1270)

## Summary
Severity: Unknown
Chain: EigenDA
Component: Layr-Labs/eigenda
Published: 2025-02-14
Source: https://github.com/Layr-Labs/eigenda/commit/18a7746085d481389cfab3156ce134834cb55ffd
Type: security-commit

## Details
Fix overflow on node block stale measure & store duration blocks override values when test-mode is enabled (#1270)

## Patch
### node/config.go
```diff
@@ -59,8 +59,8 @@ type Config struct {
 	RegisterNodeAtStart            bool
 	ExpirationPollIntervalSec      uint64
 	EnableTestMode                 bool
-	OverrideBlockStaleMeasure      int64
-	OverrideStoreDurationBlocks    int64
+	OverrideBlockStaleMeasure      uint64
+	OverrideStoreDurationBlocks    uint64
 	QuorumIDList                   []core.QuorumID
 	DbPath                         string
 	LogPath                        string
@@ -291,8 +291,8 @@ func NewConfig(ctx *cli.Context) (*Config, error) {
 		ExpirationPollIntervalSec:           expirationPollIntervalSec,
 		ReachabilityPollIntervalSec:         reachabilityPollIntervalSec,
 		EnableTestMode:                      testMode,
-		OverrideBlockStaleMeasure:           ctx.GlobalInt64(flags.OverrideBlockStaleMeasureFlag.Name),
-		OverrideStoreDurationBlocks:         ctx.GlobalInt64(flags.OverrideStoreDurationBlocksFlag.Name),
+		OverrideBlockStaleMeasure:           ctx.GlobalUint64(flags.OverrideBlockStaleMeasureFlag.Name),
+		OverrideStoreDurationBlocks:         ctx.GlobalUint64(flags.OverrideStoreDurationBlocksFlag.Name),
 		QuorumIDList:                        ids,
 		DbPath:                              ctx.GlobalString(flags.DbPathFlag.Name),
 		EthClientConfig:                     ethClientConfig,
```

### node/flags/flags.go
```diff
@@ -389,21 +389,21 @@ var (
 	// Corresponding to the BLOCK_STALE_MEASURE defined onchain in
 	// contracts/src/core/EigenDAServiceManagerStorage.sol
 	// This flag is used to override the value from the chain. The target use case is testing.
-	OverrideBlockStaleMeasureFlag = cli.StringFlag{
+	OverrideBlockStaleMeasureFlag = cli.Uint64Flag{
 		Name:     common.PrefixFlag(FlagPrefix, "override-block-stale-measure"),
-		Usage:    "The maximum amount of blocks in the past that the service will consider stake amounts to still be valid. This is used to override the value set on chain. <=0 means no override",
+		Usage:    "The maximum amount of blocks in the past that the service will consider stake amounts to still be valid. This is used to override the value set on chain. 0 means no override",
 		Required: false,
-		Value:    "-1",
+		Value:    0,
 		EnvVar:   common.PrefixEnvVar(EnvVarPrefix, "OVERRIDE_BLOCK_STALE_MEASURE"),
 	}
 	// Corresponding to the STORE_DURATION_BLOCKS defined onchain in
 	// contracts/src/core/EigenDAServiceManagerStorage.sol
 	// This flag is used to override the value from the chain. The target use case is testing.
-	OverrideStoreDurationBlocksFlag = cli.StringFlag{
+	OverrideStoreDurationBlocksFlag = cli.Uint64Flag{
 		Name:     common.PrefixFlag(FlagPrefix, "override-store-duration-blocks"),
-		Usage:    "Unit of measure (in blocks) for which data will be stored for after confirmation. This is used to override the value set on chain. <=0 means no override",
+		Usage:    "Unit of measure (in blocks) for which data will be stored for after confirmation. This is used to override the value set on chain. 0 means no override",
 		Required: false,
-		Value:    "-1",
+		Value:    0,
 		EnvVar:   common.PrefixEnvVar(EnvVarPrefix, "OVERRIDE_STORE_DURATION_BLOCKS"),
 	}
 	// DO NOT set plain private key in flag in production.
```
