# [?] Fixed race condition when creating app.toml (it gets created by the sdk, so creating it in the init command in the app creates it twice, causing not f

## Summary
Severity: Unknown
Chain: Secret
Component: scrtlabs/SecretNetwork
Published: 2022-11-10
Source: https://github.com/scrtlabs/SecretNetwork/commit/8dc402a1feda9f037acc0f868d1746d809f15357
Type: security-commit

## Details
Fixed race condition when creating app.toml (it gets created by the sdk, so creating it in the init command in the app creates it twice, causing not fun things to happen)

## Patch
### cmd/secretd/config.go
```diff
@@ -40,10 +40,16 @@ func initAppConfig() (string, interface{}) {
 	srvCfg.GRPCWeb.Enable = true
 	srvCfg.GRPCWeb.EnableUnsafeCORS = true
 
+	// defaulting this to false until we can verify it's amazballs
+	srvCfg.GRPC.Concurrency = false
+
 	secretAppConfig := SecretAppConfig{
 		Config:     *srvCfg,
 		WASMConfig: *compute.DefaultWasmConfig(),
 	}
+	secretAppConfig.Config.IAVLDisableFastNode = false
+
+	secretAppConfig.WASMConfig.EnclaveCacheSize = 200
 
 	secretAppTemplate := serverconfig.DefaultConfigTemplate + compute.DefaultConfigTemplate
 
```

### cmd/secretd/init.go
```diff
@@ -11,7 +11,6 @@ import (
 
 	"github.com/cosmos/go-bip39"
 	"github.com/pkg/errors"
-	"github.com/scrtlabs/SecretNetwork/x/compute"
 	"github.com/spf13/cobra"
 	tmconfig "github.com/tendermint/tendermint/config"
 
@@ -24,7 +23,6 @@ import (
 	"github.com/cosmos/cosmos-sdk/client/flags"
 	"github.com/cosmos/cosmos-sdk/client/input"
 	"github.com/cosmos/cosmos-sdk/server"
-	sdkconfig "github.com/cosmos/cosmos-sdk/server/config"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	"github.com/cosmos/cosmos-sdk/types/module"
 	"github.com/cosmos/cosmos-sdk/x/genutil"
@@ -85,12 +83,6 @@ func InitCmd(mbm module.BasicManager, defaultNodeHome string) *cobra.Command {
 			tmConfig := serverCtx.Config
 			tmConfig.SetRoot(clientCtx.HomeDir)
 
-			// Secret Network config (.secretd/config/app.toml)
-			secretConfig := SecretAppConfig{
-				Config:     *sdkconfig.DefaultConfig(),
-				WASMConfig: *compute.DefaultWasmConfig(),
-			}
-
 			chainID, _ := cmd.Flags().GetString(flags.FlagChainID)
 			if chainID == "" {
 				chainID = fmt.Sprintf("test-chain-%s", tmrand.Str(6))
@@ -113,15 +105,6 @@ func InitCmd(mbm module.BasicManager, defaultNodeHome string) *cobra.Command {
 			tmConfig.StateSync.TrustPeriod = 112 * time.Hour
 			tmConfig.FastSync.Version = "v0"
 
-			// Assaf: This changes the default when creating app.toml in `secretd init` (E.g. on a new node)
-			secretConfig.MinGasPrices = "0.0125uscrt"
-			secretConfig.API.Enable = true
-			secretConfig.API.Swagger = true
-			secretConfig.API.EnableUnsafeCORS = true
-			secretConfig.GRPCWeb.Enable = true
-			secretConfig.GRPCWeb.EnableUnsafeCORS = true
-			secretConfig.IAVLDisableFastNode = false
-
 			// Get bip39 mnemonic
 			var mnemonic string
 			recover, _ := cmd.Flags().GetBool(FlagRecover)
@@ -180,7 +163,6 @@ func InitCmd(mbm module.BasicManager, defaultNodeHome string) *cobra.Command {
 			toPrint := newPrintInfo(tmConfig.Moniker, chainID, nodeID, "", appState)
 
 			tmconfig.WriteConfigFile(filepath.Join(tmConfig.RootDir, "config", "config.toml"), tmConfig)
-			sdkconfig.WriteConfigFile(filepath.Join(tmConfig.RootDir, "config", "app.toml"), secretConfig)
 			return displayInfo(toPrint)
 		},
 	}
```

### cmd/secretd/root.go
```diff
@@ -159,7 +159,6 @@ func initRootCmd(rootCmd *cobra.Command, encodingConfig app.EncodingConfig) {
 
 	rootCmd.AddCommand(
 		InitCmd(app.ModuleBasics(), app.DefaultNodeHome),
-		// updateTmParamsAndInit(app.ModuleBasics(), app.DefaultNodeHome),
 		genutilcli.CollectGenTxsCmd(banktypes.GenesisBalancesIterator{}, app.DefaultNodeHome),
 		secretlegacy.MigrateGenesisCmd(),
 		genutilcli.GenTxCmd(app.ModuleBasics(), encodingConfig.TxConfig, banktypes.GenesisBalancesIterator{}, app.DefaultNodeHome),
```
