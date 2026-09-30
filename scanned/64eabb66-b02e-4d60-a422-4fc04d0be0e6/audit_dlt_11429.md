# [?] fix possible overflow of debridge.lockedInStrategies in function returnReserves

## Summary
Severity: Unknown
Chain: Bridge
Component: debridge-finance/debridge-contracts-v1
Published: 2021-08-05
Source: https://github.com/debridge-finance/debridge-contracts-v1/commit/0bb9f90e6a497bd4df384b0198718a0e941d960e
Type: security-commit

## Details
fix possible overflow of debridge.lockedInStrategies in function returnReserves

## Patch
### contracts/transfers/DeBridgeGate.sol
```diff
@@ -662,9 +662,15 @@ contract DeBridgeGate is Initializable,
                 address(this),
                 _amount
             );
-            debridge.lockedInStrategies -= _amount;
+            debridge.lockedInStrategies -=
+                _amount > debridge.lockedInStrategies
+                ? debridge.lockedInStrategies
+                : _amount;
         } else {
-            debridge.lockedInStrategies -= msg.value;
+            debridge.lockedInStrategies -=
+                msg.value > debridge.lockedInStrategies
+                ? debridge.lockedInStrategies
+                : msg.value;
         }
     }
 
```
