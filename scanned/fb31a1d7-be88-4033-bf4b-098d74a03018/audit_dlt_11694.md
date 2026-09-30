# [?] Avoid signed overflow in MSVC AMR64 secp256k1_mul128

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin-core/secp256k1
Published: 2022-11-17
Source: https://github.com/bitcoin-core/secp256k1/commit/3afce0af7c00eb4c5ca6d303e36a48c91a800459
Type: security-commit

## Details
Avoid signed overflow in MSVC AMR64 secp256k1_mul128

## Patch
### src/int128_struct_impl.h
```diff
@@ -19,7 +19,7 @@ static SECP256K1_INLINE uint64_t secp256k1_umul128(uint64_t a, uint64_t b, uint6
 
 static SECP256K1_INLINE int64_t secp256k1_mul128(int64_t a, int64_t b, int64_t* hi) {
     *hi = __mulh(a, b);
-    return a * b;
+    return (uint64_t)a * (uint64_t)b;
 }
 #    else
 /* On x84_64 MSVC, use native _(u)mul128 for 64x64->128 multiplications. */
```
