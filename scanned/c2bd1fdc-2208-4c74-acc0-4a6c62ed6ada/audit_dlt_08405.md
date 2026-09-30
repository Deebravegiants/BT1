# [?] fix(client/tx): avoid integer uint64->int64 overflow by big.Int conversion (#18622)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-12-04
Source: https://github.com/cosmos/cosmos-sdk/commit/0a7567ddc30514eedb120af160b0f5cc6b1360d8
Type: security-commit

## Details
fix(client/tx): avoid integer uint64->int64 overflow by big.Int conversion (#18622)

## Patch
### CHANGELOG.md
```diff
@@ -71,6 +71,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 ### Bug Fixes
 
+* (client) [#18622](https://github.com/cosmos/cosmos-sdk/pull/18622) Fixed a potential under/overflow from `uint64->int64` when computing gas fees as a LegacyDec.
 * (client/keys) [#18562](https://github.com/cosmos/cosmos-sdk/pull/18562) `keys delete` won't terminate when a key is not found
 * (server) [#18537](https://github.com/cosmos/cosmos-sdk/pull/18537) Fix panic when defining minimum gas config as `100stake;100uatom`. Use a `,` delimiter instead of `;`. Fixes the server config getter to use the correct delimiter.
 * [#18531](https://github.com/cosmos/cosmos-sdk/pull/18531) Baseapp's `GetConsensusParams` returns an empty struct instead of panicking if no params are found.
```

### client/tx/factory.go
```diff
@@ -3,6 +3,7 @@ package tx
 import (
 	"errors"
 	"fmt"
+	"math/big"
 	"os"
 	"strings"
 
@@ -311,7 +312,9 @@ func (f Factory) BuildUnsignedTx(msgs ...sdk.Msg) (client.TxBuilder, error) {
 			return nil, errors.New("cannot provide both fees and gas prices")
 		}
 
-		glDec := math.LegacyNewDec(int64(f.gas))
+		// f.gas is a uint64 and we should convert to LegacyDec
+		// without the risk of under/overflow via uint64->int64.
+		glDec := math.LegacyNewDecFromBigInt(new(big.Int).SetUint64(f.gas))
 
 		// Derive the fees based on the provided gas prices, where
 		// fee = ceil(gasPrice * gasLimit).
```
