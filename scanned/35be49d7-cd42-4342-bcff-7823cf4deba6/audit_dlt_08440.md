# [?] fix: `{overflow}` bug when querying cosmwasmpool spot price (#6710)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2023-10-25
Source: https://github.com/osmosis-labs/osmosis/commit/ca49a1d4236ae31434bb15ae22ce404c497a53e0
Type: security-commit

## Details
fix: `{overflow}` bug when querying cosmwasmpool spot price (#6710)

* fix cosmwasm query helper gas limit

* update osmoutils version

* update changelog

## Patch
### CHANGELOG.md
```diff
@@ -69,6 +69,7 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 * [#6666](https://github.com/osmosis-labs/osmosis/pull/6666) fix: cosmwasmpool state export bug
 * [#6674](https://github.com/osmosis-labs/osmosis/pull/6674) fix: remove dragonberry replace directive
 * [#6692](https://github.com/osmosis-labs/osmosis/pull/6692) chore: add cur sqrt price to LiquidityNetInDirection return value
+* [#6710](https://github.com/osmosis-labs/osmosis/pull/6710) fix: `{overflow}` bug when querying cosmwasmpool spot price
 
 ## v19.2.0
 
```

### go.mod
```diff
@@ -24,7 +24,7 @@ require (
 	github.com/ory/dockertest/v3 v3.10.0
 	github.com/osmosis-labs/go-mutesting v0.0.0-20221208041716-b43bcd97b3b3
 	github.com/osmosis-labs/osmosis/osmomath v0.0.7-0.20231014001935-1946419d44eb
-	github.com/osmosis-labs/osmosis/osmoutils v0.0.7-0.20231011004221-fd24b80f8366
+	github.com/osmosis-labs/osmosis/osmoutils v0.0.7-0.20231017074304-84e27b5e2aad
 	github.com/osmosis-labs/osmosis/x/epochs v0.0.3-0.20231011004221-fd24b80f8366
 	github.com/osmosis-labs/osmosis/x/ibc-hooks v0.0.9-0.20231014001935-1946419d44eb
 	github.com/pkg/errors v0.9.1
```

### go.sum
```diff
@@ -968,6 +968,8 @@ github.com/osmosis-labs/osmosis/osmomath v0.0.7-0.20231014001935-1946419d44eb h1
 github.com/osmosis-labs/osmosis/osmomath v0.0.7-0.20231014001935-1946419d44eb/go.mod h1:jNZ952fypVNMzOsh31LAUS27JbF9naNJGtELxId6ZCg=
 github.com/osmosis-labs/osmosis/osmoutils v0.0.7-0.20231011004221-fd24b80f8366 h1:EJDJ88w2Yv5LnlaJw5x53C0k/dp/fnEYOfBYOQiMsTc=
 github.com/osmosis-labs/osmosis/osmoutils v0.0.7-0.20231011004221-fd24b80f8366/go.mod h1:Zmyx5zMUBN2KV94booSFn2v8KQcUKeCHqyWpKZ4PRMo=
+github.com/osmosis-labs/osmosis/osmoutils v0.0.7-0.20231017074304-84e27b5e2aad h1:UcQ/XLz0SqWMrA+BhgDXy9ukD4C+FlN4ULdazZmFOsE=
+github.com/osmosis-labs/osmosis/osmoutils v0.0.7-0.20231017074304-84e27b5e2aad/go.mod h1:16AXMzbTLkYE5If5VLTA07fV9JNcLFwgf/VoW5sHrtU=
 github.com/osmosis-labs/osmosis/v19 v19.0.0 h1:gqcas/XfxtEuZXsWGTO9vNMHiY78Qs09FBQw73djIVM=
 github.com/osmosis-labs/osmosis/x/epochs v0.0.3-0.20231011004221-fd24b80f8366 h1:E6H0V3MKbSNwo1iXE9Kzatd2M02MgZpS5AiJ6CKK5us=
 github.com/osmosis-labs/osmosis/x/epochs v0.0.3-0.20231011004221-fd24b80f8366/go.mod h1:vU0IHK5W38dqMeux3MkSaT3MZU6whAkx7vNuxv1IzeU=
```

### osmoutils/cosmwasm/helpers.go
```diff
@@ -2,6 +2,8 @@ package cosmwasm
 
 import (
 	"encoding/json"
+
+	storetypes "github.com/cosmos/cosmos-sdk/store/types"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 )
 
@@ -26,6 +28,7 @@ type ContractKeeper interface {
 // the WasmKeeper.
 type WasmKeeper interface {
 	QuerySmart(ctx sdk.Context, contractAddress sdk.AccAddress, queryMsg []byte) ([]byte, error)
+	QueryGasLimit() storetypes.Gas
 }
 
 // Query is a generic function to query a CosmWasm smart contract with the given request.
@@ -51,6 +54,7 @@ func Query[T any, K any](ctx sdk.Context, wasmKeeper WasmKeeper, contractAddress
 		return response, err
 	}
 
+	ctx = ctx.WithGasMeter(storetypes.NewGasMeter(wasmKeeper.QueryGasLimit()))
 	responseBz, err := wasmKeeper.QuerySmart(ctx, sdk.MustAccAddressFromBech32(contractAddress), bz)
 	if err != nil {
 		return response, err
```

### x/cosmwasmpool/types/expected_keepers.go
```diff
@@ -1,6 +1,7 @@
 package types
 
 import (
+	storetypes "github.com/cosmos/cosmos-sdk/store/types"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 
 	wasmtypes "github.com/CosmWasm/wasmd/x/wasm/types"
@@ -52,6 +53,7 @@ type ContractKeeper interface {
 // the WasmKeeper.
 type WasmKeeper interface {
 	QuerySmart(ctx sdk.Context, contractAddress sdk.AccAddress, queryMsg []byte) ([]byte, error)
+	QueryGasLimit() storetypes.Gas
 
 	GetContractInfo(ctx sdk.Context, contractAddress sdk.AccAddress) *wasmtypes.ContractInfo
 }
```
