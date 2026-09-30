# [?] fix: consume gas on contract out of gas error panic (#9511)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2025-09-24
Source: https://github.com/osmosis-labs/osmosis/commit/3af7d43019e55dd8d16f01810f89c9b18e2b419f
Type: security-commit

## Details
fix: consume gas on contract out of gas error panic (#9511)

* consume gas on contract panic

* Update changelog

* trigger CI

* update code comment

## Patch
### CHANGELOG.md
```diff
@@ -54,6 +54,7 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 * [#9476](https://github.com/osmosis-labs/osmosis/pull/9476) fix: update DefaultBaseFee and cap CurBaseFee when loaded 
 * [#9488](https://github.com/osmosis-labs/osmosis/pull/9488) chore: bump block-sdk to v2.1.8-mempool
 * [#9493](https://github.com/osmosis-labs/osmosis/pull/9493) fix: update block-sdk version that fix staled mempool and add tests 
+* [#9511](https://github.com/osmosis-labs/osmosis/pull/9511) fix: tokenfactory before send hook gas consumption
 
 ## v30.0.1
 
```

### osmoutils/cosmwasm/helpers.go
```diff
@@ -61,12 +61,26 @@ func Query[T any, K any](ctx sdk.Context, wasmKeeper WasmKeeper, contractAddress
 	// Check remaining gas in parent context and use the lesser of the query gas limit and remaining gas
 	gasLimit := min(ctx.GasMeter().GasRemaining(), wasmKeeper.QueryGasLimit())
 	childCtx := ctx.WithGasMeter(storetypes.NewGasMeter(gasLimit))
-	responseBz, err := wasmKeeper.QuerySmart(childCtx, sdk.MustAccAddressFromBech32(contractAddress), bz)
-	if err != nil {
-		return response, err
-	}
 
-	ctx.GasMeter().ConsumeGas(childCtx.GasMeter().GasConsumed(), "query smart")
+	// Execute the query with proper gas tracking and panic recovery
+	var queryErr error
+	var responseBz []byte
+
+	// the immediately invoked function is used to scope down panic recovery to only the contract call
+	func() {
+		defer func() {
+			// Always consume gas from child context to parent, even if query panics
+			ctx.GasMeter().ConsumeGas(childCtx.GasMeter().GasConsumed(), "query smart")
+			if r := recover(); r != nil {
+				queryErr = fmt.Errorf("contract query ran out of gas: %v", r)
+			}
+		}()
+		responseBz, queryErr = wasmKeeper.QuerySmart(childCtx, sdk.MustAccAddressFromBech32(contractAddress), bz)
+	}()
+
+	if queryErr != nil {
+		return response, queryErr
+	}
 
 	if err := json.Unmarshal(responseBz, &response); err != nil {
 		return response, err
@@ -124,25 +138,31 @@ func Sudo[T any, K any](ctx sdk.Context, contractKeeper ContractKeeper, contract
 		return response, err
 	}
 
-	// Defer to catch panics in case the sudo call runs out of gas.
-	defer func() {
-		if r := recover(); r != nil {
-			var emptyResponse K
-			response = emptyResponse
-			err = fmt.Errorf("contract call ran out of gas")
-		}
-	}()
-
 	// Make contract call with a gas limit of 30M to ensure contracts cannot run unboundedly
 	gasLimit := min(ctx.GasMeter().Limit(), DefaultContractCallGasLimit)
 	childCtx := ctx.WithGasMeter(storetypes.NewGasMeter(gasLimit))
-	responseBz, err := contractKeeper.Sudo(childCtx, sdk.MustAccAddressFromBech32(contractAddress), bz)
-	if err != nil {
-		return response, err
-	}
 
-	// Consume gas used for calling contract to the parent ctx
-	ctx.GasMeter().ConsumeGas(childCtx.GasMeter().GasConsumed(), "Track contract call gas")
+	// Execute the contract call with proper gas tracking and panic recovery
+	var contractErr error
+	var responseBz []byte
+
+	// the immediately invoked function is used to scope down panic recovery to only the contract call
+	func() {
+		defer func() {
+			// Always consume gas from child context to parent, even if contract panics
+			ctx.GasMeter().ConsumeGas(childCtx.GasMeter().GasConsumed(), "Track contract call gas")
+			if r := recover(); r != nil {
+				var emptyResponse K
+				response = emptyResponse
+				contractErr = fmt.Errorf("contract call ran out of gas: %v", r)
+			}
+		}()
+		responseBz, contractErr = contractKeeper.Sudo(childCtx, sdk.MustAccAddressFromBech32(contractAddress), bz)
+	}()
+
+	if contractErr != nil {
+		return response, contractErr
+	}
 
 	// valid empty response
 	if len(responseBz) == 0 {
```

### x/concentrated-liquidity/pool_hooks.go
```diff
@@ -129,13 +129,25 @@ func (k Keeper) callPoolActionListener(ctx sdk.Context, msgBuilderFn msgBuilderF
 	// Check remaining gas in parent context and use the lesser of the hook gas limit and remaining gas
 	gasLimit := min(ctx.GasMeter().GasRemaining(), k.GetParams(ctx).HookGasLimit)
 	childCtx := ctx.WithGasMeter(storetypes.NewGasMeter(gasLimit))
-	_, err = k.contractKeeper.Sudo(childCtx.WithEventManager(em), cwAddr, msgBz)
-	if err != nil {
-		return err
-	}
 
-	// Consume gas used for calling contract to the parent ctx
-	ctx.GasMeter().ConsumeGas(childCtx.GasMeter().GasConsumed(), "Track CL action contract call gas")
+	// Execute the contract call with proper gas tracking and panic recovery
+	var contractErr error
+
+	// the immediately invoked function is used to scope down panic recovery to only the contract call
+	func() {
+		defer func() {
+			// Always consume gas from child context to parent, even if contract panics
+			ctx.GasMeter().ConsumeGas(childCtx.GasMeter().GasConsumed(), "Track CL action contract call gas")
+			if r := recover(); r != nil {
+				contractErr = types.ContractHookOutOfGasError{GasLimit: k.GetParams(ctx).HookGasLimit}
+			}
+		}()
+		_, contractErr = k.contractKeeper.Sudo(childCtx.WithEventManager(em), cwAddr, msgBz)
+	}()
+
+	if contractErr != nil {
+		return contractErr
+	}
 
 	return nil
 }
```

### x/tokenfactory/keeper/before_send.go
```diff
@@ -166,7 +166,20 @@ func (k Keeper) callBeforeSendListener(context context.Context, from, to sdk.Acc
 			gasLimit := min(ctx.GasMeter().GasRemaining(), types.BeforeSendHookGasLimit)
 
 			childCtx := ctx.WithGasMeter(storetypes.NewGasMeter(gasLimit))
-			_, err = k.contractKeeper.Sudo(childCtx.WithEventManager(em), cwAddr, msgBz)
+
+			// Execute the contract call with proper gas tracking and panic recovery
+
+			func() {
+				defer func() {
+					// Always consume gas from child context to parent, even if contract panics
+					ctx.GasMeter().ConsumeGas(childCtx.GasMeter().GasConsumed(), "track before send gas")
+					if r := recover(); r != nil {
+						err = errorsmod.Wrapf(types.ErrBeforeSendHookOutOfGas, "%v", r)
+					}
+				}()
+				_, err = k.contractKeeper.Sudo(childCtx.WithEventManager(em), cwAddr, msgBz)
+			}()
+
 			if err != nil {
 				if strings.Contains(err.Error(), "no such contract") {
 					return nil
@@ -177,9 +190,6 @@ func (k Keeper) callBeforeSendListener(context context.Context, from, to sdk.Acc
 
 				return errorsmod.Wrapf(err, "failed to call before send hook for denom %s", coin.Denom)
 			}
-
-			// consume gas used for calling contract to the parent ctx
-			ctx.GasMeter().ConsumeGas(childCtx.GasMeter().GasConsumed(), "track before send gas")
 		}
 	}
 	return nil
```

### x/tokenfactory/keeper/before_send_test.go
```diff
@@ -277,3 +277,38 @@ func (s *KeeperTestSuite) TestInfiniteTrackBeforeSend() {
 		})
 	}
 }
+
+func (s *KeeperTestSuite) TestCallBeforeSendListenerGasConsumption() {
+	s.SetupTest()
+
+	// upload infinite loop wasm contract to trigger out of gas
+	wasmCode, err := os.ReadFile("./testdata/infinite_track_beforesend.wasm")
+	s.Require().NoError(err)
+	codeID, _, err := s.contractKeeper.Create(s.Ctx, s.TestAccs[0], wasmCode, nil)
+	s.Require().NoError(err)
+	cosmwasmAddress, _, err := s.contractKeeper.Instantiate(s.Ctx, codeID, s.TestAccs[0], s.TestAccs[0], []byte("{}"), "", sdk.NewCoins())
+	s.Require().NoError(err)
+
+	// create factory denom
+	res, err := s.msgServer.CreateDenom(s.Ctx, types.NewMsgCreateDenom(s.TestAccs[0].String(), "testcoin"))
+	s.Require().NoError(err)
+	denom := res.GetNewTokenDenom()
+
+	// set before send hook
+	_, err = s.msgServer.SetBeforeSendHook(s.Ctx, types.NewMsgSetBeforeSendHook(s.TestAccs[0].String(), denom, cosmwasmAddress.String()))
+	s.Require().NoError(err)
+
+	// measure gas consumption before and after BlockBeforeSend
+	hooks := s.App.TokenFactoryKeeper.Hooks()
+	amount := sdk.NewCoins(sdk.NewInt64Coin(denom, 100))
+
+	// record gas consumed before calling BlockBeforeSend
+	gasConsumedBefore := s.Ctx.GasMeter().GasConsumed()
+
+	err = hooks.BlockBeforeSend(s.Ctx, s.TestAccs[0], s.TestAccs[1], amount)
+
+	// record gas consumed after calling BlockBeforeSend
+	gasConsumedAfter := s.Ctx.GasMeter().GasConsumed()
+	gasUsed := gasConsumedAfter - gasConsumedBefore
+	s.Require().Equal(gasUsed, uint64(501435))
+}
```
