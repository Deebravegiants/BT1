# [?] Fix possible integer overflow in DER parsing

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin-core/secp256k1
Published: 2018-11-01
Source: https://github.com/bitcoin-core/secp256k1/commit/3cb057f8429c812b5dbfcd43299658463162b740
Type: security-commit

## Details
Fix possible integer overflow in DER parsing

If we’re in the last loop iteration, then `lenleft == 1` and it could
be the case that `ret == MAX_SIZE`, and so `ret +  lenleft` will
overflow to 0 and the sanity check will not catch it. Then we will
return `(int) MAX_SIZE`, which should be avoided because this value is
implementation-defined. (However, this is harmless because
`(int) MAX_SIZE == -1` on all supported platforms.)

## Patch
### src/ecdsa_impl.h
```diff
@@ -66,7 +66,7 @@ static int secp256k1_der_read_len(const unsigned char **sigp, const unsigned cha
         return -1;
     }
     /* X.690-207 8.1.3.5 long form length octets */
-    lenleft = b1 & 0x7F;
+    lenleft = b1 & 0x7F; /* lenleft is at least 1 */
     if (lenleft > sigend - *sigp) {
         return -1;
     }
@@ -82,13 +82,13 @@ static int secp256k1_der_read_len(const unsigned char **sigp, const unsigned cha
     }
     while (lenleft > 0) {
         ret = (ret << 8) | **sigp;
-        if (ret + lenleft > (size_t)(sigend - *sigp)) {
-            /* Result exceeds the length of the passed array. */
-            return -1;
-        }
         (*sigp)++;
         lenleft--;
     }
+    if (ret > (size_t)(sigend - *sigp)) {
+        /* Result exceeds the length of the passed array. */
+        return -1;
+    }
     if (ret < 128) {
         /* Not the shortest possible length encoding. */
         return -1;
```
