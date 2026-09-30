# [?] Fix tests for the vulnerability to have no timestamp

## Summary
Severity: Unknown
Chain: Curve
Component: curvefi/curve-contract
Published: 2020-01-27
Source: https://github.com/curvefi/curve-contract/commit/3c1e265786b83aeca157c37fc263b3e32fac2d92
Type: security-commit

## Details
Fix tests for the vulnerability to have no timestamp

## Patch
### tests/test_exchange.py
```diff
@@ -38,18 +38,14 @@ def test_few_trades(w3, coins, cerc20s, swap, pool_token):
     # And trades
     with pytest.raises(TransactionFailed):
         # Cannot exchange to the same currency
-        swap.functions.exchange_underlying(
-            0, 0, 1 * UU[0], 0, int(time.time()) + 3600
-        ).transact(from_bob)
+        swap.functions.exchange_underlying(0, 0, 1 * UU[0], 0).transact(from_bob)
 
     test_amount = deposits[0] // 10
     assert cerc20s[0].caller.balanceOf(sam) > test_amount
     assert cerc20s[0].caller.allowance(sam, swap.address) > test_amount
     with pytest.raises(TransactionFailed):
         # Cannot exchange to the same here, too
-        swap.functions.exchange(
-            0, 0, test_amount, 0, int(time.time()) + 3600
-        ).transact(from_sam)
+        swap.functions.exchange(0, 0, test_amount, 0).transact(from_sam)
 
     swap.functions.exchange_underlying(
         0, 1, 1 * UU[0], int(0.9 * UU[1])
@@ -77,15 +73,11 @@ def test_few_trades(w3, coins, cerc20s, swap, pool_token):
 
     # Cannot exchange now
     with pytest.raises(TransactionFailed):
-        swap.functions.exchange_underlying(
-            0, 1, 1 * UU[0], 0, int(time.time()) + 3600
-        ).transact(from_bob)
+        swap.functions.exchange_underlying(0, 1, 1 * UU[0], 0).transact(from_bob)
 
     # But can withdraw
     value = pool_token.caller.balanceOf(sam)
-    swap.functions.remove_liquidity(
-        value, int(time.time()) + 3600, [0] * N_COINS
-    ).transact(from_sam)
+    swap.functions.remove_liquidity(value, [0] * N_COINS).transact(from_sam)
 
 
 def test_simulated_exchange(w3, coins, cerc20s, swap):
```
