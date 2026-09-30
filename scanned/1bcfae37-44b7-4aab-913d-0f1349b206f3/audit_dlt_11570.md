# [?] Fixed bug where getLiquidationPrice method would crash if proposed position size was zero

## Summary
Severity: Unknown
Chain: Solana
Component: velocity-exchange/protocol-v2
Published: 2021-12-24
Source: https://github.com/velocity-exchange/protocol-v2/commit/78348dc38a6136c9f2fd50f2f231750b18f18cde
Type: security-commit

## Details
Fixed bug where getLiquidationPrice method would crash if proposed position size was zero

## Patch
### sdk/src/clearingHouseUser.ts
```diff
@@ -588,6 +588,8 @@ export class ClearingHouseUser {
 			) {
 				return new BN(-1);
 			}
+
+			if (proposedBaseAssetAmount.eq(ZERO)) return new BN(-1);
 	
 			const eatMargin2 = priceDelt.mul(AMM_RESERVE_PRECISION).div(proposedBaseAssetAmount);
 	
```
