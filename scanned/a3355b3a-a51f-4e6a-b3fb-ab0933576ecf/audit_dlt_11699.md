# [?] Prevent damage_array in the signature test from going out of bounds.

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin-core/secp256k1
Published: 2015-11-26
Source: https://github.com/bitcoin-core/secp256k1/commit/5d4c5a31b9ca5d7f85d1ea211f44d93279f41fea
Type: security-commit

## Details
Prevent damage_array in the signature test from going out of bounds.

## Patch
### src/tests.c
```diff
@@ -3607,13 +3607,13 @@ static void assign_big_endian(unsigned char *ptr, size_t ptrlen, uint32_t val) {
 static void damage_array(unsigned char *sig, size_t *len) {
     int pos;
     int action = secp256k1_rand_bits(3);
-    if (action < 1) {
+    if (action < 1 && *len > 3) {
         /* Delete a byte. */
         pos = secp256k1_rand_int(*len);
         memmove(sig + pos, sig + pos + 1, *len - pos - 1);
         (*len)--;
         return;
-    } else if (action < 2) {
+    } else if (action < 2 && *len < 2048) {
         /* Insert a byte. */
         pos = secp256k1_rand_int(1 + *len);
         memmove(sig + pos + 1, sig + pos, *len - pos);
@@ -3785,6 +3785,7 @@ void run_ecdsa_der_parse(void) {
         int certainly_der = 0;
         int certainly_not_der = 0;
         random_ber_signature(buffer, &buflen, &certainly_der, &certainly_not_der);
+        CHECK(buflen <= 2048);
         for (j = 0; j < 16; j++) {
             int ret = 0;
             if (j > 0) {
```
