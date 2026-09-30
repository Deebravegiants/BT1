# [?] Comments on how to prevent overflow

## Summary
Severity: Unknown
Chain: Curve
Component: curvefi/curve-contract
Published: 2019-09-17
Source: https://github.com/curvefi/curve-contract/commit/eaa26bb83e1b2e1225fdb74cc3913a3ca36b0a6d
Type: security-commit

## Details
Comments on how to prevent overflow

## Patch
### vyper/stableswap.vy
```diff
@@ -29,6 +29,7 @@ future_owner: public(address)
 def __init__(a: address, b: address,
              amplification: uint256, _fee: uint256):
     assert a != ZERO_ADDRESS and b != ZERO_ADDRESS
+    # XXX TODO: use up 10 digits of decimal
     self.coin_a = a
     self.coin_b = b
     self.X = convert(amplification, decimal)
@@ -123,30 +124,46 @@ def cbrt(x: decimal) -> decimal:
 
 @private
 @constant
-def D() -> decimal:
+def get_D() -> decimal:
     """
-    Constant D by solving a cubic equation, using Cardaon formula
+    Constant D by solving a cubic equation, using Cardano formula
     """
     x: decimal = convert(self.quantity_a, decimal)
     y: decimal = convert(self.quantity_b, decimal)
     A: decimal = self.X
     p: decimal = (16.0 * A - 4.0) * x * y
     q: decimal = -16.0 * A * x * y * (x + y)
-    Disc: decimal = sqrt(q*q / 4.0 + p*p*p / 27.0)
-    return self.cbrt(-q / 2.0 + Disc) - self.cbrt(q / 2.0 + Disc)
+    Disc: decimal = sqrt(q*q / 4.0 + p*p*p / 27.0)  # take xy out
+    return self.cbrt(-q / 2.0 + Disc) - self.cbrt(q / 2.0 + Disc)  # and here
+    # Gives about 1e20 - enough precision, hopefully?
+    # Not compatible with hyper-inflation - too bad for Zimbabwe
+    # Need to switch to integers also
 
 @public
 @constant
 def get_price(from_coin: address, to_coin: address) -> decimal:
     if self.quantity_a == 0 and self.quantity_b == 0:
         return 1.0
     # XXX
+    x: uint256 = 1000
+    y: uint256 = sqrt256(x)
     return 1.0
 
 @public
 @constant
 def get_volume(from_coin: address, to_coin: address,
                from_amount: uint256) -> uint256:
+    x: decimal
+    y: decimal
+    if from_coin == self.coin_a and to_coin == self.coin_b:
+        x = convert(self.quantity_a, decimal)
+        y = convert(self.quantity_b, decimal)
+    elif from_coin == self.coin_b and to_coin == self.coin_a:
+        y = convert(self.quantity_a, decimal)
+        x = convert(self.quantity_b, decimal)
+    else:
+        raise "Unknown coin"
+    dx: decimal = convert(from_amount, decimal)
     return 0
 
 @public
```
