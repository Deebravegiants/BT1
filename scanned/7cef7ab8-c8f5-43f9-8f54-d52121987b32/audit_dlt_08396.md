# [?] fix(simapp/v2): panic with testnet init-files command (#21012)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2024-07-22
Source: https://github.com/cosmos/cosmos-sdk/commit/f9f2ad7fa96b3cb2a52ecd3d6d5e8b927ee62009
Type: security-commit

## Details
fix(simapp/v2): panic with testnet init-files command (#21012)

## Patch
### simapp/v2/simdv2/cmd/root_test.go
```diff
@@ -7,11 +7,11 @@ import (
 	"github.com/stretchr/testify/require"
 
 	"cosmossdk.io/core/transaction"
+	svrcmd "cosmossdk.io/server/v2"
 	"cosmossdk.io/simapp/v2"
 	"cosmossdk.io/simapp/v2/simdv2/cmd"
 
 	"github.com/cosmos/cosmos-sdk/client/flags"
-	svrcmd "github.com/cosmos/cosmos-sdk/server/cmd"
 	"github.com/cosmos/cosmos-sdk/x/genutil/client/cli"
 )
 
```

### simapp/v2/simdv2/cmd/testnet.go
```diff
@@ -198,7 +198,7 @@ func initTestnetFiles[T transaction.Tx](
 	// generate private keys, node IDs, and initial transactions
 	for i := 0; i < args.numValidators; i++ {
 		var portOffset int
-		var grpcConfig *grpc.Config
+		grpcConfig := grpc.DefaultConfig()
 		if args.singleMachine {
 			portOffset = i
 			p2pPortStart = 16656 // use different start point to not conflict with rpc port
```

### simapp/v2/simdv2/cmd/testnet_test.go
```diff
@@ -0,0 +1,27 @@
+package cmd_test
+
+import (
+	"fmt"
+	"testing"
+
+	"github.com/stretchr/testify/require"
+
+	"cosmossdk.io/core/transaction"
+	svrcmd "cosmossdk.io/server/v2"
+	"cosmossdk.io/simapp/v2"
+	"cosmossdk.io/simapp/v2/simdv2/cmd"
+
+	"github.com/cosmos/cosmos-sdk/client/flags"
+	"github.com/cosmos/cosmos-sdk/crypto/keyring"
+)
+
+func TestInitTestFilesCmd(t *testing.T) {
+	rootCmd := cmd.NewRootCmd[transaction.Tx]()
+	rootCmd.SetArgs([]string{
+		"testnet", // Test the testnet init-files command
+		"init-files",
+		fmt.Sprintf("--%s=%s", flags.FlagKeyringBackend, keyring.BackendTest), // Set keyring-backend to test
+	})
+
+	require.NoError(t, svrcmd.Execute(rootCmd, "", simapp.DefaultNodeHome))
+}
```
