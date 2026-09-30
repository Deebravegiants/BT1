# [?] fix module to not return error, just panic #ntrn-328

## Summary
Severity: Unknown
Chain: Neutron
Component: neutron-org/neutron
Published: 2023-01-26
Source: https://github.com/neutron-org/neutron/commit/4299b4b2a17fab094def7a57da4ebe8d5ea9d082
Type: security-commit

## Details
fix module to not return error, just panic #ntrn-328

## Patch
### x/feeburner/keeper/keeper.go
```diff
@@ -84,7 +84,7 @@ func (k Keeper) GetTotalBurnedNeutronsAmount(ctx sdk.Context) types.TotalBurnedN
 // 2. Updates total amount of burned NTRN coins
 // 3. Sends non-NTRN fee tokens to treasury contract address
 // Panics if no `consumertypes.ConsumerRedistributeName` module found OR could not burn NTRN tokens
-func (k Keeper) BurnAndDistribute(ctx sdk.Context) error {
+func (k Keeper) BurnAndDistribute(ctx sdk.Context) {
 	moduleAddr := k.accountKeeper.GetModuleAddress(consumertypes.ConsumerRedistributeName)
 	if moduleAddr == nil {
 		panic("ConsumerRedistributeName must have module address")
@@ -116,11 +116,9 @@ func (k Keeper) BurnAndDistribute(ctx sdk.Context) error {
 			fundsForTreasury,
 		)
 		if err != nil {
-			return fmt.Errorf("error sending funds to treasury for address=%s, tokens=%+v: %v", params.TreasuryAddress, fundsForTreasury, err)
+			panic(sdkerrors.Wrapf(err, "failed sending funds to treasury"))
 		}
 	}
-
-	return nil
 }
 
 func (k Keeper) Logger(ctx sdk.Context) log.Logger {
```

### x/feeburner/keeper/keeper_test.go
```diff
@@ -2,6 +2,7 @@ package keeper_test
 
 import (
 	"fmt"
+	"github.com/stretchr/testify/assert"
 	"testing"
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
@@ -98,8 +99,7 @@ func TestKeeper_BurnAndDistribute_Clean(t *testing.T) {
 	defer ctrl.Finish()
 	feeKeeper, ctx, _, _ := setupBurnAndDistribute(t, ctrl, sdk.Coins{})
 
-	err := feeKeeper.BurnAndDistribute(ctx)
-	require.NoError(t, err)
+	feeKeeper.BurnAndDistribute(ctx)
 
 	burnedAmount := feeKeeper.GetTotalBurnedNeutronsAmount(ctx)
 	require.Equal(t, burnedAmount.Coin.Amount, sdk.NewInt(0))
@@ -112,8 +112,7 @@ func TestKeeper_BurnAndDistribute_Ntrn(t *testing.T) {
 
 	mockBankKeeper.EXPECT().BurnCoins(ctx, consumertypes.ConsumerRedistributeName, sdk.Coins{sdk.NewCoin(feetypes.DefaultNeutronDenom, sdk.NewInt(100))})
 
-	err := feeKeeper.BurnAndDistribute(ctx)
-	require.NoError(t, err)
+	feeKeeper.BurnAndDistribute(ctx)
 
 	burnedAmount := feeKeeper.GetTotalBurnedNeutronsAmount(ctx)
 	require.Equal(t, burnedAmount.Coin.Amount, sdk.NewInt(100))
@@ -126,8 +125,7 @@ func TestKeeper_BurnAndDistribute_NonNtrn(t *testing.T) {
 
 	mockBankKeeper.EXPECT().SendCoins(ctx, redistrAddr, sdk.MustAccAddressFromBech32(feeKeeper.GetParams(ctx).TreasuryAddress), sdk.Coins{sdk.NewCoin("nonntrn", sdk.NewInt(50))})
 
-	err := feeKeeper.BurnAndDistribute(ctx)
-	require.NoError(t, err)
+	feeKeeper.BurnAndDistribute(ctx)
 
 	burnedAmount := feeKeeper.GetTotalBurnedNeutronsAmount(ctx)
 	require.Equal(t, burnedAmount.Coin.Amount, sdk.NewInt(0))
@@ -140,8 +138,9 @@ func TestKeeper_BurnAndDistribute_SendCoinsFail(t *testing.T) {
 
 	mockBankKeeper.EXPECT().SendCoins(ctx, redistrAddr, sdk.MustAccAddressFromBech32(feeKeeper.GetParams(ctx).TreasuryAddress), sdk.Coins{sdk.NewCoin("nonntrn", sdk.NewInt(50))}).Return(fmt.Errorf("testerror"))
 
-	err := feeKeeper.BurnAndDistribute(ctx)
-	require.ErrorContains(t, err, "error sending funds to treasury for address")
+	assert.Panics(t, func() {
+		feeKeeper.BurnAndDistribute(ctx)
+	}, "did not panic")
 
 	burnedAmount := feeKeeper.GetTotalBurnedNeutronsAmount(ctx)
 	require.Equal(t, burnedAmount.Coin.Amount, sdk.NewInt(0))
@@ -156,8 +155,7 @@ func TestKeeper_BurnAndDistribute_NtrnAndNonNtrn(t *testing.T) {
 	mockBankKeeper.EXPECT().BurnCoins(ctx, consumertypes.ConsumerRedistributeName, sdk.Coins{sdk.NewCoin(feetypes.DefaultNeutronDenom, sdk.NewInt(70))})
 	mockBankKeeper.EXPECT().SendCoins(ctx, redistrAddr, sdk.MustAccAddressFromBech32(feeKeeper.GetParams(ctx).TreasuryAddress), sdk.Coins{sdk.NewCoin("nonntrn", sdk.NewInt(20))})
 
-	err := feeKeeper.BurnAndDistribute(ctx)
-	require.NoError(t, err)
+	feeKeeper.BurnAndDistribute(ctx)
 	burnedAmount := feeKeeper.GetTotalBurnedNeutronsAmount(ctx)
 	require.Equal(t, burnedAmount.Coin.Amount, sdk.NewInt(70))
 }
```

### x/feeburner/module.go
```diff
@@ -153,13 +153,6 @@ func (am AppModule) BeginBlock(_ sdk.Context, _ abci.RequestBeginBlock) {}
 
 // EndBlock contains the logic that is automatically triggered at the end of each block
 func (am AppModule) EndBlock(ctx sdk.Context, _ abci.RequestEndBlock) []abci.ValidatorUpdate {
-	err := am.keeper.BurnAndDistribute(ctx)
-	if err != nil {
-		ctx.Logger().Error(
-			"feeburner: EndBlock: failed to send tokens to Treasury",
-			"error", err,
-		)
-	}
-
+	am.keeper.BurnAndDistribute(ctx)
 	return []abci.ValidatorUpdate{}
 }
```
