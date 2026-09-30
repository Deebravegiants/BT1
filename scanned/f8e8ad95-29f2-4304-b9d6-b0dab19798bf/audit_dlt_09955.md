# [?] fix panic(err) if posted_prices=[] in genesis file (#352)

## Summary
Severity: Unknown
Chain: Kava
Component: Kava-Labs/kava
Published: 2020-01-30
Source: https://github.com/Kava-Labs/kava/commit/3c8209cbcc01f5d5b544a0f51558f136d8499c65
Type: security-commit

## Details
fix panic(err) if posted_prices=[] in genesis file (#352)

## Patch
### x/pricefeed/genesis.go
```diff
@@ -25,9 +25,12 @@ func InitGenesis(ctx sdk.Context, keeper Keeper, gs GenesisState) {
 	// Set the current price (if any) based on what's now in the store
 	for _, market := range params.Markets {
 		if market.Active {
-			err := keeper.SetCurrentPrices(ctx, market.MarketID)
-			if err != nil {
-				panic(err)
+			rps := keeper.GetRawPrices(ctx, market.MarketID)
+			if len(rps) > 0 {
+				err := keeper.SetCurrentPrices(ctx, market.MarketID)
+				if err != nil {
+					panic(err)
+				}
 			}
 		}
 	}
```
