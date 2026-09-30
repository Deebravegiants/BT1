# [?] overflow/underflow checks in FixedPointExtra.sol#muluq

## Summary
Severity: Unknown
Chain: Uniswap
Component: Uniswap/v3-core
Published: 2020-08-20
Source: https://github.com/Uniswap/v3-core/commit/1bbabbebae084437c894067ab455b6e56df76e00
Type: security-commit

## Details
overflow/underflow checks in FixedPointExtra.sol#muluq

## Patch
### contracts/libraries/FixedPointExtra.sol
```diff
@@ -23,19 +23,31 @@ library FixedPointExtra {
         pure
         returns (FixedPoint.uq112x112 memory)
     {
-        uint224 upper_self = self._x >> 112; // * 2^0
-        uint224 lower_self = self._x & LOWER_MASK; // * 2^-112
-        uint224 upper_other = other._x >> 112; // * 2^0
-        uint224 lower_other = other._x & LOWER_MASK; // * 2^-112
+        if (self._x == 0 || other._x == 0) {
+            return FixedPoint.uq112x112(0);
+        }
+        uint112 upper_self = uint112(self._x >> 112); // * 2^0
+        uint112 lower_self = uint112(self._x & LOWER_MASK); // * 2^-112
+        uint112 upper_other = uint112(other._x >> 112); // * 2^0
+        uint112 lower_other = uint112(other._x & LOWER_MASK); // * 2^-112
 
         // partial products
-        uint224 uppers = upper_self * upper_other; // * 2^0
-        uint224 lowers = lower_self * lower_other; // * 2^-224
-        uint224 uppers_lowero = upper_self * lower_other; // * 2^-112
-        uint224 uppero_lowers = upper_other * lower_self; // * 2^-112
+        uint224 uppers = uint224(upper_self) * upper_other; // * 2^0
+        uint224 lowers = uint224(lower_self) * lower_other; // * 2^-224
+        uint224 uppers_lowero = uint224(upper_self) * lower_other; // * 2^-112
+        uint224 uppero_lowers = uint224(upper_other) * lower_self; // * 2^-112
 
+        // so the bit shift does not overflow
+        require(uppers <= uint112(-1), "FixedPointExtra: MULTIPLICATION_OVERFLOW");
+
+        // this cannot exceed 256 bits, all values are 224 bits
         uint sum = uint(uppers << 112) + uppers_lowero + uppero_lowers + (lowers >> 112);
+
+        // between 224 bits and 256 bits
         require(sum <= uint224(-1), "FixedPointExtra: MULTIPLICATION_OVERFLOW");
+
+        // the multiplication results in a number too small to be represented in Q112.112
+        require(sum > 0, "FixedPointExtra: MULTIPLICATION_UNDERFLOW");
         return FixedPoint.uq112x112(uint224(sum));
     }
 
```

### test/FixedPointExtra.spec.ts
```diff
@@ -12,7 +12,7 @@ const overrides = {
 
 const Q112 = BigNumber.from(2).pow(112)
 
-describe('FixedPointExtra', () => {
+describe.only('FixedPointExtra', () => {
   const provider = new MockProvider({
     ganacheOptions: {
       hardfork: 'istanbul',
@@ -40,8 +40,20 @@ describe('FixedPointExtra', () => {
       )
     })
 
+    it('throws for underflow', async () => {
+      await expect(fixedPointExtra.muluq([BigNumber.from(1)], [BigNumber.from(1)])).to.be.revertedWith(
+        'FixedPointExtra: MULTIPLICATION_UNDERFLOW'
+      )
+    })
+
+    it('throws for overflow', async () => {
+      await expect(
+        fixedPointExtra.muluq([Q112.mul(BigNumber.from(2).pow(56))], [Q112.mul(BigNumber.from(2).pow(56))])
+      ).to.be.revertedWith('FixedPointExtra: MULTIPLICATION_OVERFLOW')
+    })
+
     it('gas', async () => {
-      expect(await fixedPointExtra.muluqGasUsed([Q112.mul(35).div(10)], [Q112.mul(22).div(10)])).to.eq('446')
+      expect(await fixedPointExtra.muluqGasUsed([Q112.mul(35).div(10)], [Q112.mul(22).div(10)])).to.eq('686')
     })
   })
 
@@ -59,7 +71,7 @@ describe('FixedPointExtra', () => {
     })
 
     it('gas', async () => {
-      expect(await fixedPointExtra.divuqGasUsed([Q112.mul(35).div(10)], [Q112.mul(22).div(10)])).to.eq('800')
+      expect(await fixedPointExtra.divuqGasUsed([Q112.mul(35).div(10)], [Q112.mul(22).div(10)])).to.eq('1040')
     })
   })
 })
```
