# [?] fix panic on uint64 conversion in evm ApplyMessageWithConfig function (#1703)

## Summary
Severity: Unknown
Chain: Evmos
Component: evmos/evmos
Published: 2023-08-16
Source: https://github.com/evmos/evmos/commit/1722c602426b3adbe0ae0a9ef5071032101aea4f
Type: security-commit

## Details
fix panic on uint64 conversion in evm ApplyMessageWithConfig function (#1703)

Co-authored-by: Vladislav Varadinov <vladislav.varadinov@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -57,6 +57,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 - (rpc) [#1676](https://github.com/evmos/evmos/pull/1676) Fix gas meter stacking gas from predecessors in `TraceTx` & `TraceBlock` functions.
 - (cli) [#1681](https://github.com/evmos/evmos/pull/1681) Add `bootstrap-state` command.
 - (ante) [#1693](https://github.com/evmos/evmos/pull/1693) Prevent panic on int64 conversion in EVM fees antehandler.
+- (evm) [#1693](https://github.com/evmos/evmos/pull/1703) Prevent panic on uint64 conversion in EVM keeper `ApplyMessageWithConfig` function.
 
 ## [v13.0.2] - 2023-07-05
 
```

### x/evm/keeper/state_transition.go
```diff
@@ -414,6 +414,10 @@ func (k *Keeper) ApplyMessageWithConfig(ctx sdk.Context,
 	minGasMultiplier := k.GetMinGasMultiplier(ctx)
 	minimumGasUsed := gasLimit.Mul(minGasMultiplier)
 
+	if !minimumGasUsed.TruncateInt().IsUint64() {
+		return nil, errorsmod.Wrapf(types.ErrGasOverflow, "minimumGasUsed(%s) is not a uint64", minimumGasUsed.TruncateInt().String())
+	}
+
 	if msg.Gas() < leftoverGas {
 		return nil, errorsmod.Wrapf(types.ErrGasOverflow, "message gas limit < leftover gas (%d < %d)", msg.Gas(), leftoverGas)
 	}
```

### x/evm/keeper/state_transition_test.go
```diff
@@ -631,6 +631,28 @@ func (suite *KeeperTestSuite) TestApplyMessageWithConfig() {
 			},
 			true,
 		},
+		{
+			"fix panic when minimumGasUsed is not uint64",
+			func() {
+				msg, err = newNativeMessage(
+					vmdb.GetNonce(suite.address),
+					suite.ctx.BlockHeight(),
+					suite.address,
+					chainCfg,
+					suite.signer,
+					signer,
+					ethtypes.AccessListTxType,
+					nil,
+					nil,
+				)
+				suite.Require().NoError(err)
+				params := suite.app.FeeMarketKeeper.GetParams(suite.ctx)
+				params.MinGasMultiplier = sdk.NewDec(math.MaxInt64).MulInt64(100)
+				err = suite.app.FeeMarketKeeper.SetParams(suite.ctx, params)
+				suite.Require().NoError(err)
+			},
+			true,
+		},
 	}
 
 	for _, tc := range testCases {
```
