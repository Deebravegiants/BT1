# [?] fix: index out of bounds

## Summary
Severity: Unknown
Chain: Curve
Component: curvefi/curve-contract
Published: 2020-10-01
Source: https://github.com/curvefi/curve-contract/commit/c0b5a6de03a906743d451a030a2a649dea23763a
Type: security-commit

## Details
fix: index out of bounds

## Patch
### contracts/pool-templates/meta/DepositTemplateMeta.vy
```diff
@@ -1,4 +1,4 @@
-# @version ^0.2.0
+# @version ^0.2.5
 # (c) Curve.Fi, 2020
 # Deposit zap for the metapool
 #
@@ -124,7 +124,7 @@ def add_liquidity(amounts: uint256[N_ALL_COINS], min_mint_amount: uint256) -> ui
             if i < MAX_COIN:
                 meta_amounts[i] = amount
             else:
-                base_amounts[i] = amount
+                base_amounts[i - MAX_COIN] = amount
 
     # Deposit to the base pool
     if deposit_base:
```

### contracts/pool-templates/meta/SwapTemplateMeta.vy
```diff
@@ -1,4 +1,4 @@
-# @version ^0.2.0
+# @version ^0.2.5
 # (c) Curve.Fi, 2020
 # Metapool
 #
```
