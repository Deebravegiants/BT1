# [?] fix order cancellation to prevent read-only reentrancy

## Summary
Severity: Unknown
Chain: GMX
Component: gmx-io/gmx-synthetics
Published: 2023-06-05
Source: https://github.com/gmx-io/gmx-synthetics/commit/6bd217f0b46f4b8fac0a9338f49075b1f29742b6
Type: security-commit

## Details
fix order cancellation to prevent read-only reentrancy

## Patch
### contracts/order/OrderUtils.sol
```diff
@@ -227,6 +227,8 @@ library OrderUtils {
         Order.Props memory order = OrderStoreUtils.get(dataStore, key);
         BaseOrderUtils.validateNonEmptyOrder(order);
 
+        OrderStoreUtils.remove(dataStore, key, order.account());
+
         if (BaseOrderUtils.isIncreaseOrder(order.orderType()) || BaseOrderUtils.isSwapOrder(order.orderType())) {
             if (order.initialCollateralDeltaAmount() > 0) {
                 orderVault.transferOut(
@@ -238,8 +240,6 @@ library OrderUtils {
             }
         }
 
-        OrderStoreUtils.remove(dataStore, key, order.account());
-
         OrderEventUtils.emitOrderCancelled(eventEmitter, key, reason, reasonBytes);
 
         EventUtils.EventLogData memory eventData;
```
