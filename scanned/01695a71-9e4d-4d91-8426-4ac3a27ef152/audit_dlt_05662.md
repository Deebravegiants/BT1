# [?] Fix prysmctl panic when baseFee is not set in genesis.json (#15687)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2025-09-18
Source: https://github.com/OffchainLabs/prysm/commit/6b89d839f630b486829668d9ad644d4386c96d33
Type: security-commit

## Details
Fix prysmctl panic when baseFee is not set in genesis.json (#15687)

* Fix prysmctl panic when baseFee is not set in genesis.json

* update add unit test

---------

Co-authored-by: james-prysm <90280386+james-prysm@users.noreply.github.com>

## Patch
### changelog/muzry_fix_prysmctl_panics.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Fix prysmctl panic when baseFee is not set in genesis.json
```

### cmd/prysmctl/testnet/BUILD.bazel
```diff
@@ -34,7 +34,11 @@ go_test(
     deps = [
         "//crypto/bls:go_default_library",
         "//runtime/interop:go_default_library",
+        "//runtime/version:go_default_library",
         "//testing/assert:go_default_library",
         "//testing/require:go_default_library",
+        "@com_github_ethereum_go_ethereum//core:go_default_library",
+        "@com_github_ethereum_go_ethereum//core/types:go_default_library",
+        "@com_github_ethereum_go_ethereum//params:go_default_library",
     ],
 )
```

### cmd/prysmctl/testnet/generate_genesis.go
```diff
@@ -279,6 +279,14 @@ func generateGenesis(ctx context.Context) (state.BeaconState, error) {
 		if v > version.Altair {
 			// set ttd to zero so EL goes post-merge immediately
 			gen.Config.TerminalTotalDifficulty = big.NewInt(0)
+			if gen.BaseFee == nil {
+				return nil, errors.New("baseFeePerGas must be set in genesis.json for Post-Merge networks (after Altair)")
+			}
+		} else {
+			if gen.BaseFee == nil {
+				gen.BaseFee = big.NewInt(1000000000) // 1 Gwei default
+				log.WithField("baseFeePerGas", "1000000000").Warn("BaseFeePerGas not specified in genesis.json, using default value of 1 Gwei")
+			}
 		}
 	} else {
 		gen = interop.GethTestnetGenesis(time.Unix(int64(f.GenesisTime), 0), params.BeaconConfig())
```

### cmd/prysmctl/testnet/generate_genesis_test.go
```diff
@@ -1,14 +1,21 @@
 package testnet
 
 import (
+	"context"
 	"encoding/json"
 	"fmt"
+	"math/big"
+	"os"
 	"testing"
 
 	"github.com/OffchainLabs/prysm/v6/crypto/bls"
 	"github.com/OffchainLabs/prysm/v6/runtime/interop"
+	"github.com/OffchainLabs/prysm/v6/runtime/version"
 	"github.com/OffchainLabs/prysm/v6/testing/assert"
 	"github.com/OffchainLabs/prysm/v6/testing/require"
+	"github.com/ethereum/go-ethereum/core"
+	"github.com/ethereum/go-ethereum/core/types"
+	"github.com/ethereum/go-ethereum/params"
 )
 
 func Test_genesisStateFromJSONValidators(t *testing.T) {
@@ -48,3 +55,76 @@ func createGenesisDepositData(t *testing.T, numKeys int) []*depositDataJSON {
 	}
 	return jsonData
 }
+
+func Test_generateGenesis_BaseFeeValidation(t *testing.T) {
+	tests := []struct {
+		name        string
+		forkVersion int
+		baseFee     *big.Int
+		expectError bool
+		errorMsg    string
+	}{
+		{
+			name:        "Pre-merge Altair network without baseFee - should use default",
+			forkVersion: version.Altair,
+			baseFee:     nil,
+			expectError: false,
+		},
+		{
+			name:        "Post-merge Bellatrix network without baseFee - should error",
+			forkVersion: version.Bellatrix,
+			baseFee:     nil,
+			expectError: true,
+			errorMsg:    "baseFeePerGas must be set in genesis.json for Post-Merge networks (after Altair)",
+		},
+	}
+
+	for _, tt := range tests {
+		t.Run(tt.name, func(t *testing.T) {
+			// Save original flags
+			originalFlags := generateGenesisStateFlags
+			defer func() {
+				generateGenesisStateFlags = originalFlags
+			}()
+
+			// Set up test flags
+			generateGenesisStateFlags.NumValidators = 2
+			generateGenesisStateFlags.GenesisTime = 1609459200
+			generateGenesisStateFlags.ForkName = version.String(tt.forkVersion)
+
+			// Create a minimal genesis JSON for testing
+			genesis := &core.Genesis{
+				BaseFee:    tt.baseFee,
+				Difficulty: big.NewInt(0),
+				GasLimit:   15000000,
+				Alloc:      types.GenesisAlloc{},
+				Config: &params.ChainConfig{
+					ChainID: big.NewInt(32382),
+				},
+			}
+
+			// Create temporary genesis JSON file
+			genesisJSON, err := json.Marshal(genesis)
+			require.NoError(t, err)
+
+			tmpFile := t.TempDir() + "/genesis.json"
+			err = writeFile(tmpFile, genesisJSON)
+			require.NoError(t, err)
+
+			generateGenesisStateFlags.GethGenesisJsonIn = tmpFile
+
+			ctx := context.Background()
+			_, err = generateGenesis(ctx)
+
+			if tt.expectError {
+				require.ErrorContains(t, tt.errorMsg, err)
+			} else {
+				require.NoError(t, err)
+			}
+		})
+	}
+}
+
+func writeFile(path string, data []byte) error {
+	return os.WriteFile(path, data, 0644)
+}
```
