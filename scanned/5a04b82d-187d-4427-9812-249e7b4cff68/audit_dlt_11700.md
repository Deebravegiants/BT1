# [?] Avoid constructing an invalid signature with probability 1:2^256.

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin-core/secp256k1
Published: 2014-12-29
Source: https://github.com/bitcoin-core/secp256k1/commit/d26e26f2f46edc35404bc9cfdcfc39daca465b0c
Type: security-commit

## Details
Avoid constructing an invalid signature with probability 1:2^256.

## Patch
### src/ecdsa_impl.h
```diff
@@ -198,6 +198,12 @@ static int secp256k1_ecdsa_sig_sign(secp256k1_ecdsa_sig_t *sig, const secp256k1_
     secp256k1_fe_get_b32(b, &r.x);
     int overflow = 0;
     secp256k1_scalar_set_b32(&sig->r, b, &overflow);
+    if (secp256k1_scalar_is_zero(&sig->r)) {
+        /* P.x = order is on the curve, so technically sig->r could end up zero, which would be an invalid signature. */
+        secp256k1_gej_clear(&rp);
+        secp256k1_ge_clear(&r);
+        return 0;
+    }
     if (recid)
         *recid = (overflow ? 2 : 0) | (secp256k1_fe_is_odd(&r.y) ? 1 : 0);
     secp256k1_scalar_t n;
```
