# [?] Audit and fix all potential uint64 overflow sites (#1197)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2023-12-29
Source: https://github.com/sei-protocol/sei-chain/commit/62b3b9e0d02e508b91df5a469aa2a4a580ab20ae
Type: security-commit

## Details
Audit and fix all potential uint64 overflow sites (#1197)

Co-authored-by: Yiming Zang <50607998+yzang2019@users.noreply.github.com>

## Patch
### x/dex/ante.go
```diff
@@ -2,6 +2,7 @@ package dex
 
 import (
 	"errors"
+	"math/big"
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	sdkacltypes "github.com/cosmos/cosmos-sdk/types/accesscontrol"
@@ -142,7 +143,7 @@ func (d CheckDexGasDecorator) AnteHandle(ctx sdk.Context, tx sdk.Tx, simulate bo
 	if dexGasRequired == 0 {
 		return next(ctx, tx, simulate)
 	}
-	dexFeeRequired := sdk.NewDecWithPrec(int64(dexGasRequired), 0).Mul(params.SudoCallGasPrice).RoundInt()
+	dexFeeRequired := sdk.NewDecFromBigInt(new(big.Int).SetUint64(dexGasRequired)).Mul(params.SudoCallGasPrice).RoundInt()
 	feeTx, ok := tx.(sdk.FeeTx)
 	if !ok {
 		return ctx, sdkerrors.Wrap(sdkerrors.ErrTxDecode, "Tx must be a FeeTx")
```

### x/dex/contract/abci.go
```diff
@@ -317,7 +317,7 @@ func TransferRentFromDexToCollector(ctx sdk.Context, bankKeeper bankkeeper.Keepe
 			total += preRent
 		}
 	}
-	if err := bankKeeper.SendCoinsFromModuleToModule(ctx, types.ModuleName, authtypes.FeeCollectorName, sdk.NewCoins(sdk.NewCoin("usei", sdk.NewInt(int64(total))))); err != nil {
+	if err := bankKeeper.SendCoinsFromModuleToModule(ctx, types.ModuleName, authtypes.FeeCollectorName, sdk.NewCoins(sdk.NewCoin("usei", sdk.NewIntFromUint64(total)))); err != nil {
 		ctx.Logger().Error("sending coins from dex to fee collector failed due to %s", err)
 	}
 }
```

### x/dex/contract/execution.go
```diff
@@ -190,16 +190,14 @@ func HandleExecutionForContract(
 }
 
 // Emit metrics for settlements
-func EmitSettlementMetrics(settlements []*types.SettlementEntry) int64 {
+func EmitSettlementMetrics(settlements []*types.SettlementEntry) {
 	if len(settlements) > 0 {
 		telemetry.ModuleSetGauge(
 			types.ModuleName,
 			float32(len(settlements)),
 			"num_settlements",
 		)
-		var totalQuantity int64
 		for _, s := range settlements {
-			totalQuantity += s.Quantity.RoundInt().Int64()
 			telemetry.IncrCounter(
 				1,
 				"num_settlements_order_type_"+s.GetOrderType(),
@@ -217,12 +215,5 @@ func EmitSettlementMetrics(settlements []*types.SettlementEntry) int64 {
 				"num_settlements_price_denom_"+s.GetPriceDenom(),
 			)
 		}
-		telemetry.ModuleSetGauge(
-			types.ModuleName,
-			float32(totalQuantity),
-			"num_total_order_quantity_in_settlements",
-		)
-		return totalQuantity
 	}
-	return 0
 }
```

### x/dex/contract/execution_test.go
```diff
@@ -369,6 +369,5 @@ func TestEmitSettlementMetrics(t *testing.T) {
 		},
 	}
 
-	totalQuantity := contract.EmitSettlementMetrics(settlements)
-	require.Equal(t, int64(300), totalQuantity)
+	require.NotPanics(t, func() { contract.EmitSettlementMetrics(settlements) })
 }
```

### x/dex/exchange/limit_order.go
```diff
@@ -2,7 +2,6 @@ package exchange
 
 import (
 	"fmt"
-	"math"
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	"github.com/sei-protocol/sei-chain/x/dex/keeper"
@@ -15,7 +14,7 @@ func MatchLimitOrders(
 ) ExecutionOutcome {
 	settlements := []*types.SettlementEntry{}
 	totalExecuted, totalPrice := sdk.ZeroDec(), sdk.ZeroDec()
-	minPrice, maxPrice := sdk.NewDecFromInt(sdk.NewIntFromUint64(math.MaxInt64)), sdk.OneDec().Neg()
+	minPrice, maxPrice := sdk.OneDec().Neg(), sdk.OneDec().Neg()
 
 	for longEntry, shortEntry := orderbook.Longs.Next(ctx), orderbook.Shorts.Next(ctx); longEntry != nil && shortEntry != nil && longEntry.GetPrice().GTE(shortEntry.GetPrice()); longEntry, shortEntry = orderbook.Longs.Next(ctx), orderbook.Shorts.Next(ctx) {
 		var executed sdk.Dec
@@ -30,7 +29,9 @@ func MatchLimitOrders(
 				longEntry.GetPrice().Add(shortEntry.GetPrice()),
 			),
 		)
-		minPrice = sdk.MinDec(minPrice, shortEntry.GetPrice())
+		if minPrice.IsNegative() || minPrice.GT(shortEntry.GetPrice()) {
+			minPrice = shortEntry.GetPrice()
+		}
 		maxPrice = sdk.MaxDec(maxPrice, longEntry.GetPrice())
 
 		newSettlements := SettleFromBook(
```

### x/dex/exchange/market_order.go
```diff
@@ -1,8 +1,6 @@
 package exchange
 
 import (
-	"math"
-
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	cache "github.com/sei-protocol/sei-chain/x/dex/cache"
 	"github.com/sei-protocol/sei-chain/x/dex/types"
@@ -16,7 +14,7 @@ func MatchMarketOrders(
 	blockOrders *cache.BlockOrders,
 ) ExecutionOutcome {
 	totalExecuted, totalPrice := sdk.ZeroDec(), sdk.ZeroDec()
-	minPrice, maxPrice := sdk.NewDecFromInt(sdk.NewIntFromUint64(math.MaxInt64)), sdk.OneDec().Neg()
+	minPrice, maxPrice := sdk.OneDec().Neg(), sdk.OneDec().Neg()
 	settlements := []*types.SettlementEntry{}
 	allTakerSettlements := []*types.SettlementEntry{}
 	for _, marketOrder := range marketOrders {
@@ -86,7 +84,9 @@ func MatchMarketOrder(
 		*totalPrice = totalPrice.Add(
 			executed.Mul(entry.GetPrice()),
 		)
-		*minPrice = sdk.MinDec(*minPrice, entry.GetPrice())
+		if minPrice.IsNegative() || minPrice.GT(entry.GetPrice()) {
+			*minPrice = entry.GetPrice()
+		}
 		*maxPrice = sdk.MaxDec(*maxPrice, entry.GetPrice())
 
 		takerSettlements, makerSettlements := Settle(
@@ -174,7 +174,9 @@ func MatchFOKMarketOrder(
 			*totalPrice = totalPrice.Add(
 				executedQuantities[i].Mul(entryPrices[i]),
 			)
-			*minPrice = sdk.MinDec(*minPrice, entryPrices[i])
+			if minPrice.IsNegative() || minPrice.GT(entryPrices[i]) {
+				*minPrice = entryPrices[i]
+			}
 			*maxPrice = sdk.MaxDec(*maxPrice, entryPrices[i])
 		}
 	} else {
@@ -247,7 +249,9 @@ func MatchByValueFOKMarketOrder(
 			*totalPrice = totalPrice.Add(
 				executedQuantities[i].Mul(entryPrices[i]),
 			)
-			*minPrice = sdk.MinDec(*minPrice, entryPrices[i])
+			if minPrice.IsNegative() || minPrice.GT(entryPrices[i]) {
+				*minPrice = entryPrices[i]
+			}
 			*maxPrice = sdk.MaxDec(*maxPrice, entryPrices[i])
 		}
 	} else {
```

### x/dex/keeper/contract.go
```diff
@@ -2,6 +2,8 @@ package keeper
 
 import (
 	"errors"
+	"math"
+	"math/big"
 	"time"
 
 	"github.com/cosmos/cosmos-sdk/store/prefix"
@@ -67,7 +69,10 @@ func (k Keeper) GetContractGasLimit(ctx sdk.Context, contractAddr sdk.AccAddress
 	if gasPrice.LTE(sdk.ZeroDec()) {
 		return 0, errors.New("invalid gas price: must be positive")
 	}
-	gasDec := sdk.NewDec(int64(rentBalance)).Quo(gasPrice)
+	gasDec := sdk.NewDecFromBigInt(new(big.Int).SetUint64(rentBalance)).Quo(gasPrice)
+	if gasDec.GT(sdk.NewDecFromBigInt(new(big.Int).SetUint64(math.MaxUint64))) {
+		return math.MaxUint64, nil
+	}
 	return gasDec.TruncateInt().Uint64(), nil // round down
 }
 
@@ -100,15 +105,19 @@ func (k Keeper) ChargeRentForGas(ctx sdk.Context, contractAddr string, gasUsed u
 		return err
 	}
 	params := k.GetParams(ctx)
-	gasFee := sdk.NewDec(int64(gasUsed)).Mul(params.SudoCallGasPrice).RoundInt().Int64()
-	if gasFee > int64(contract.RentBalance) {
+	gasFeeDec := sdk.NewDecFromBigInt(new(big.Int).SetUint64(gasUsed)).Mul(params.SudoCallGasPrice)
+	if gasFeeDec.GT(sdk.NewDecFromBigInt(new(big.Int).SetUint64(math.MaxUint64))) {
+		gasFeeDec = sdk.NewDecFromBigInt(new(big.Int).SetUint64(math.MaxUint64))
+	}
+	gasFee := gasFeeDec.RoundInt().Uint64()
+	if gasFee > contract.RentBalance {
 		contract.RentBalance = 0
 		if err := k.SetContract(ctx, &contract); err != nil {
 			return err
 		}
 		return types.ErrInsufficientRent
 	}
-	contract.RentBalance -= uint64(gasFee)
+	contract.RentBalance -= gasFee
 	return k.SetContract(ctx, &contract)
 }
 
@@ -126,7 +135,7 @@ func (k Keeper) GetRentsForContracts(ctx sdk.Context, contractAddrs []string) ma
 func (k Keeper) DoUnregisterContractWithRefund(ctx sdk.Context, contract types.ContractInfoV2) error {
 	k.DoUnregisterContract(ctx, contract)
 	creatorAddr, _ := sdk.AccAddressFromBech32(contract.Creator)
-	return k.BankKeeper.SendCoins(ctx, k.AccountKeeper.GetModuleAddress(types.ModuleName), creatorAddr, sdk.NewCoins(sdk.NewCoin(appparams.BaseCoinUnit, sdk.NewInt(int64(contract.RentBalance)))))
+	return k.BankKeeper.SendCoins(ctx, k.AccountKeeper.GetModuleAddress(types.ModuleName), creatorAddr, sdk.NewCoins(sdk.NewCoin(appparams.BaseCoinUnit, sdk.NewIntFromBigInt(new(big.Int).SetUint64(contract.RentBalance)))))
 }
 
 // Contract unregistration will remove all orderbook data stored for the contract
```

### x/dex/keeper/contract_test.go
```diff
@@ -1,6 +1,7 @@
 package keeper_test
 
 import (
+	"math"
 	"testing"
 
 	"github.com/cosmos/cosmos-sdk/store/prefix"
@@ -126,6 +127,20 @@ func TestGetContractGasLimit(t *testing.T) {
 	gasLimit, err := keeper.GetContractGasLimit(ctx, contractAddr)
 	require.Nil(t, err)
 	require.Equal(t, uint64(10000000), gasLimit)
+
+	params := keeper.GetParams(ctx)
+	params.SudoCallGasPrice = sdk.NewDecWithPrec(1, 1) // 0.1
+	keeper.SetParams(ctx, params)
+	keeper.SetContract(ctx, &types.ContractInfoV2{
+		Creator:      keepertest.TestAccount,
+		ContractAddr: "sei1suhgf5svhu4usrurvxzlgn54ksxmn8gljarjtxqnapv8kjnp4nrsgshtdj",
+		CodeId:       1,
+		RentBalance:  math.MaxUint64,
+	})
+	gasLimit, err = keeper.GetContractGasLimit(ctx, contractAddr)
+	require.Nil(t, err)
+	// max uint64 / 0.1 would cause overflow so we cap it at max
+	require.Equal(t, uint64(math.MaxUint64), gasLimit)
 }
 
 func TestGetRentsForContracts(t *testing.T) {
```

### x/dex/keeper/msgserver/msg_server_contract_deposit_rent.go
```diff
@@ -38,7 +38,7 @@ func (k msgServer) ContractDepositRent(goCtx context.Context, msg *types.MsgCont
 	if err != nil {
 		return nil, err
 	}
-	if err := k.BankKeeper.SendCoins(ctx, senderAddr, k.AccountKeeper.GetModuleAddress(types.ModuleName), sdk.NewCoins(sdk.NewCoin(appparams.BaseCoinUnit, sdk.NewInt(int64(msg.Amount))))); err != nil {
+	if err := k.BankKeeper.SendCoins(ctx, senderAddr, k.AccountKeeper.GetModuleAddress(types.ModuleName), sdk.NewCoins(sdk.NewCoin(appparams.BaseCoinUnit, sdk.NewIntFromUint64(msg.Amount)))); err != nil {
 		return nil, err
 	}
 
```

### x/dex/keeper/msgserver/msg_server_register_contract.go
```diff
@@ -200,7 +200,7 @@ func (k msgServer) HandleDepositOrRefund(ctx sdk.Context, msg *types.MsgRegister
 	if existingContract, err := k.GetContract(ctx, msg.Contract.ContractAddr); err != nil {
 		// brand new contract
 		if msg.Contract.RentBalance > 0 {
-			if err := k.BankKeeper.SendCoins(ctx, creatorAddr, k.AccountKeeper.GetModuleAddress(types.ModuleName), sdk.NewCoins(sdk.NewCoin(appparams.BaseCoinUnit, sdk.NewInt(int64(msg.Contract.RentBalance))))); err != nil {
+			if err := k.BankKeeper.SendCoins(ctx, creatorAddr, k.AccountKeeper.GetModuleAddress(types.ModuleName), sdk.NewCoins(sdk.NewCoin(appparams.BaseCoinUnit, sdk.NewIntFromUint64(msg.Contract.RentBalance)))); err != nil {
 				return err
 			}
 		}
@@ -211,13 +211,13 @@ func (k msgServer) HandleDepositOrRefund(ctx sdk.Context, msg *types.MsgRegister
 		if msg.Contract.RentBalance < existingContract.RentBalance {
 			// refund
 			refundAmount := existingContract.RentBalance - msg.Contract.RentBalance
-			if err := k.BankKeeper.SendCoins(ctx, k.AccountKeeper.GetModuleAddress(types.ModuleName), creatorAddr, sdk.NewCoins(sdk.NewCoin(appparams.BaseCoinUnit, sdk.NewInt(int64(refundAmount))))); err != nil {
+			if err := k.BankKeeper.SendCoins(ctx, k.AccountKeeper.GetModuleAddress(types.ModuleName), creatorAddr, sdk.NewCoins(sdk.NewCoin(appparams.BaseCoinUnit, sdk.NewIntFromUint64(refundAmount)))); err != nil {
 				return err
 			}
 		} else if msg.Contract.RentBalance > existingContract.RentBalance {
 			// deposit
 			depositAmount := msg.Contract.RentBalance - existingContract.RentBalance
-			if err := k.BankKeeper.SendCoins(ctx, creatorAddr, k.AccountKeeper.GetModuleAddress(types.ModuleName), sdk.NewCoins(sdk.NewCoin(appparams.BaseCoinUnit, sdk.NewInt(int64(depositAmount))))); err != nil {
+			if err := k.BankKeeper.SendCoins(ctx, creatorAddr, k.AccountKeeper.GetModuleAddress(types.ModuleName), sdk.NewCoins(sdk.NewCoin(appparams.BaseCoinUnit, sdk.NewIntFromUint64(depositAmount)))); err != nil {
 				return err
 			}
 		}
```
