# [?] fix panic bug "Int64() out of bound" in ante handler (#1693)

## Summary
Severity: Unknown
Chain: Evmos
Component: evmos/evmos
Published: 2023-08-11
Source: https://github.com/evmos/evmos/commit/74594fb8a8f58cb01f2a02b0ccbceaab922c8934
Type: security-commit

## Details
fix panic bug "Int64() out of bound" in ante handler (#1693)

* fix panic bug "Int64() out of bound" in ante handler

* update CHANGELOG.md

## Patch
### CHANGELOG.md
```diff
@@ -51,6 +51,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 - (rpc) [#1663](https://github.com/evmos/evmos/pull/1663) Fix block number returned in opcode for debug trace related api.
 - (rpc) [#1676](https://github.com/evmos/evmos/pull/1676) Fix gas meter stacking gas from predecessors in `TraceTx` & `TraceBlock` functions.
 - (cli) [#1681](https://github.com/evmos/evmos/pull/1681) Add `bootstrap-state` command.
+- (ante) [#1693](https://github.com/evmos/evmos/pull/1693) Prevent panic on int64 conversion in EVM fees antehandler.
 
 ## [v13.0.2] - 2023-07-05
 
```

### app/ante/evm/fees.go
```diff
@@ -100,8 +100,8 @@ func (empd EthMinGasPriceDecorator) AnteHandle(ctx sdk.Context, tx sdk.Tx, simul
 		if fee.LT(requiredFee) {
 			return ctx, errorsmod.Wrapf(
 				errortypes.ErrInsufficientFee,
-				"provided fee < minimum global fee (%d < %d). Please increase the priority tip (for EIP-1559 txs) or the gas prices (for access list or legacy txs)", //nolint:lll
-				fee.TruncateInt().Int64(), requiredFee.TruncateInt().Int64(),
+				"provided fee < minimum global fee (%s < %s). Please increase the priority tip (for EIP-1559 txs) or the gas prices (for access list or legacy txs)", //nolint:lll
+				fee.TruncateInt().String(), requiredFee.TruncateInt().String(),
 			)
 		}
 	}
```

### app/ante/evm/fees_test.go
```diff
@@ -1,6 +1,7 @@
 package evm_test
 
 import (
+	"math"
 	"math/big"
 
 	sdkmath "cosmossdk.io/math"
@@ -227,6 +228,20 @@ func (suite *AnteTestSuite) TestEthMinGasPriceDecorator() {
 			true,
 			"",
 		},
+		{
+			"panic bug, requiredFee > math.MaxInt64",
+			func() sdk.Tx {
+				params := suite.app.FeeMarketKeeper.GetParams(suite.ctx)
+				params.MinGasPrice = sdk.NewDec(math.MaxInt64)
+				err := suite.app.FeeMarketKeeper.SetParams(suite.ctx, params)
+				suite.Require().NoError(err)
+
+				msg := suite.BuildTestEthTx(from, to, nil, make([]byte, 0), nil, big.NewInt(math.MaxInt64), big.NewInt(100), &emptyAccessList)
+				return suite.CreateTestTx(msg, privKey, 1, false)
+			},
+			false,
+			"provided fee < minimum global fee",
+		},
 	}
 
 	for _, et := range execTypes {
```
