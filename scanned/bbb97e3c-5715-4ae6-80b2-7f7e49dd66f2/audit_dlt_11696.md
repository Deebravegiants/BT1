# [?] Avoid out-of-bound pointers and integer overflows in size comparisons

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin-core/secp256k1
Published: 2018-11-07
Source: https://github.com/bitcoin-core/secp256k1/commit/ec8f20babd8595f119e642d3833ee90bacc12873
Type: security-commit

## Details
Avoid out-of-bound pointers and integer overflows in size comparisons

This changes pointer calculations in size comparions to a form that
ensures that no out-of-bound pointers are computed, because even their
computation yields undefined behavior.
Also, this changes size comparions to a form that ensures that neither
the left-hand side nor the right-hand side can overflow.

## Patch
### contrib/lax_der_parsing.c
```diff
@@ -32,7 +32,7 @@ int ecdsa_signature_parse_der_lax(const secp256k1_context* ctx, secp256k1_ecdsa_
     lenbyte = input[pos++];
     if (lenbyte & 0x80) {
         lenbyte -= 0x80;
-        if (pos + lenbyte > inputlen) {
+        if (lenbyte > inputlen - pos) {
             return 0;
         }
         pos += lenbyte;
@@ -51,7 +51,7 @@ int ecdsa_signature_parse_der_lax(const secp256k1_context* ctx, secp256k1_ecdsa_
     lenbyte = input[pos++];
     if (lenbyte & 0x80) {
         lenbyte -= 0x80;
-        if (pos + lenbyte > inputlen) {
+        if (lenbyte > inputlen - pos) {
             return 0;
         }
         while (lenbyte > 0 && input[pos] == 0) {
@@ -89,7 +89,7 @@ int ecdsa_signature_parse_der_lax(const secp256k1_context* ctx, secp256k1_ecdsa_
     lenbyte = input[pos++];
     if (lenbyte & 0x80) {
         lenbyte -= 0x80;
-        if (pos + lenbyte > inputlen) {
+        if (lenbyte > inputlen - pos) {
             return 0;
         }
         while (lenbyte > 0 && input[pos] == 0) {
```

### src/ecdsa_impl.h
```diff
@@ -157,12 +157,8 @@ static int secp256k1_ecdsa_sig_parse(secp256k1_scalar *rr, secp256k1_scalar *rs,
     if (secp256k1_der_read_len(&rlen, &sig, sigend) == 0) {
         return 0;
     }
-    if (sig + rlen > sigend) {
-        /* Tuple exceeds bounds */
-        return 0;
-    }
-    if (sig + rlen != sigend) {
-        /* Garbage after tuple. */
+    if (rlen != (size_t)(sigend - sig)) {
+        /* Tuple exceeds bounds or garage after tuple. */
         return 0;
     }
 
```

### src/hash_impl.h
```diff
@@ -131,7 +131,8 @@ static void secp256k1_sha256_transform(uint32_t* s, const uint32_t* chunk) {
 static void secp256k1_sha256_write(secp256k1_sha256 *hash, const unsigned char *data, size_t len) {
     size_t bufsize = hash->bytes & 0x3F;
     hash->bytes += len;
-    while (bufsize + len >= 64) {
+    VERIFY_CHECK(hash->bytes >= len);
+    while (len >= 64 - bufsize) {
         /* Fill the buffer, and process it. */
         size_t chunk_len = 64 - bufsize;
         memcpy(((unsigned char*)hash->buf) + bufsize, data, chunk_len);
```
