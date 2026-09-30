# [?] sdk: fix fuelInsurance type on overflow account

## Summary
Severity: Unknown
Chain: Solana
Component: velocity-exchange/protocol-v2
Published: 2025-03-05
Source: https://github.com/velocity-exchange/protocol-v2/commit/3299c5845dd0f424185cf89a40b905a072f25512
Type: security-commit

## Details
sdk: fix fuelInsurance type on overflow account

## Patch
### sdk/src/types.ts
```diff
@@ -1011,7 +1011,7 @@ export type UserStatsAccount = {
 
 export type FuelOverflowAccount = {
 	authority: PublicKey;
-	fuelInsurance: number;
+	fuelInsurance: BN;
 	fuelDeposits: BN;
 	fuelBorrows: BN;
 	fuelPositions: BN;
```
