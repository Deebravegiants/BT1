# [?] fix overflow in case order collateral delta exceeds position collateral amount

## Summary
Severity: Unknown
Chain: GMX
Component: gmx-io/gmx-synthetics
Published: 2023-08-18
Source: https://github.com/gmx-io/gmx-synthetics/commit/fcf296a73661b2c5f8c0605b4ae668f0b24f9bb5
Type: security-commit

## Details
fix overflow in case order collateral delta exceeds position collateral amount

## Patch
### contracts/position/DecreasePositionUtils.sol
```diff
@@ -94,6 +94,18 @@ library DecreasePositionUtils {
             }
         }
 
+        // cap the initialCollateralDeltaAmount to the position collateralAmount
+        if (params.order.initialCollateralDeltaAmount() > params.position.collateralAmount()) {
+            OrderEventUtils.emitOrderCollateralDeltaAmountAutoUpdated(
+                params.contracts.eventEmitter,
+                params.orderKey,
+                params.order.initialCollateralDeltaAmount(),
+                params.position.collateralAmount()
+            );
+
+            params.order.setInitialCollateralDeltaAmount(params.position.collateralAmount());
+        }
+
         // if the position will be partially decreased then do a check on the
         // remaining collateral amount and update the order attributes if needed
         if (params.order.sizeDeltaUsd() < params.position.sizeInUsd()) {
```
