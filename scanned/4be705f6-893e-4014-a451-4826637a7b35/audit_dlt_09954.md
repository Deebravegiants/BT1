# [?] fix: avoid panic when closing cdp via repayment (#353)

## Summary
Severity: Unknown
Chain: Kava
Component: Kava-Labs/kava
Published: 2020-01-30
Source: https://github.com/Kava-Labs/kava/commit/bdff81b2a261fe847cef143dac81ecdceab4c1a6
Type: security-commit

## Details
fix: avoid panic when closing cdp via repayment (#353)

## Patch
### x/cdp/keeper/cdp.go
```diff
@@ -110,7 +110,7 @@ func (k Keeper) MintDebtCoins(ctx sdk.Context, moduleAccount string, denom strin
 	return nil
 }
 
-// BurnDebtCoins burns debts coins from the cdp module account
+// BurnDebtCoins burns debt coins from the cdp module account
 func (k Keeper) BurnDebtCoins(ctx sdk.Context, moduleAccount string, denom string, paymentCoins sdk.Coins) sdk.Error {
 	coinsToBurn := sdk.NewCoins()
 	for _, pc := range paymentCoins {
```

### x/cdp/keeper/draw.go
```diff
@@ -110,7 +110,16 @@ func (k Keeper) RepayPrincipal(ctx sdk.Context, owner sdk.AccAddress, denom stri
 	}
 
 	// burn the corresponding amount of debt coins
-	err = k.BurnDebtCoins(ctx, types.ModuleName, k.GetDebtDenom(ctx), feePayment.Add(principalPayment))
+	cdpDebt := k.getModAccountDebt(ctx, types.ModuleName)
+	paymentAmount := sdk.ZeroInt()
+	for _, c := range feePayment.Add(principalPayment) {
+		paymentAmount = paymentAmount.Add(c.Amount)
+	}
+	coinsToBurn := sdk.NewCoins(sdk.NewCoin(k.GetDebtDenom(ctx), paymentAmount))
+	if paymentAmount.GT(cdpDebt) {
+		coinsToBurn = sdk.NewCoins(sdk.NewCoin(k.GetDebtDenom(ctx), cdpDebt))
+	}
+	err = k.BurnDebtCoins(ctx, types.ModuleName, k.GetDebtDenom(ctx), coinsToBurn)
 	if err != nil {
 		panic(err)
 	}
```
