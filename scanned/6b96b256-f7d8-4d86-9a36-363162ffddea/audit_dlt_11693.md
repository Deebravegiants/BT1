# [?] Merge bitcoin-core/secp256k1#1821: ellswift: fix overflow flag handling in secp256k1_ellswift_xdh

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin-core/secp256k1
Published: 2026-02-17
Source: https://github.com/bitcoin-core/secp256k1/commit/c7a7f732bd17c71499341af77966c7ee2e75956c
Type: security-commit

## Details
Merge bitcoin-core/secp256k1#1821: ellswift: fix overflow flag handling in secp256k1_ellswift_xdh

b99a94c3827e1b8e8505648758512eb3cf4aae03 Add tests for bad scalar inputs in ellswift XDH (gzJx0DuTRHytnHe7P5RmMbPf3wKy2BztweVGXTf)
307b49f1b996024d458a9b69e9df8d15b628d34a ellswift: fix overflow flag handling in secp256k1_ellswift_xdh (gzJx0DuTRHytnHe7P5RmMbPf3wKy2BztweVGXTf)

Pull request description:

  The secp256k1_ellswift_xdh function uses overflow = secp256k1_scalar_is_zero(&s) which overwrites the overflow flag from the preceding secp256k1_scalar_set_b32 call. This means secret keys >= the curve order are silently accepted (reduced mod n) instead of being rejected.

  The fix changes = to |=, matching the correct pattern already used in secp256k1_ecdh (main_impl.h, line 51).

  The ECDH module's test suite explicitly tests overflow rejection (passes secp256k1_group_order_bytes as a key and checks the function returns 0). The ellswift test suite has no corresponding test, which is why this went undetected.

  Previous PR to the wrong repository: https://github.com/bitcoin/bitcoin/pull/34558

ACKs for top commit:
  kevkevinpal:
    ACK b99a94c3827e1b8e8505648758512eb3cf4aae03
  real-or-random:
    utACK b99a94c3827e1b8e8505648758512eb3cf4aae03
  theStack:
    re-ACK b99a94c3827e1b8e8505648758512eb3cf4aae03

Tree-SHA512: 6222cd7616c7429f4c05180257f925720b7f9743fa440667a2327f94cb134a160cdf498dca1713ffc470ab3a6ca3275aafbd14b2e790766fe10ddb5ce6970e80

## Patch
### src/modules/ellswift/main_impl.h
```diff
@@ -564,7 +564,7 @@ int secp256k1_ellswift_xdh(const secp256k1_context *ctx, unsigned char *output,
 
     /* Load private key (using one if invalid). */
     secp256k1_scalar_set_b32(&s, seckey32, &overflow);
-    overflow = secp256k1_scalar_is_zero(&s);
+    overflow |= secp256k1_scalar_is_zero(&s);
     secp256k1_scalar_cmov(&s, &secp256k1_scalar_one, overflow);
 
     /* Compute shared X coordinate. */
```

### src/modules/ellswift/tests_impl.h
```diff
@@ -460,6 +460,33 @@ void ellswift_hash_init_tests(void) {
     test_sha256_tag_midstate(&sha_optimized, bip324_tag, sizeof(bip324_tag));
 }
 
+void ellswift_xdh_bad_scalar_tests(void) {
+    unsigned char s_zero[32] = { 0 };
+    unsigned char s_overflow_minus1[32] = { 0 };
+    unsigned char s_overflow_plus1[32] = { 0 };
+    unsigned char s_good[32] = { 0 };
+    unsigned char ell_a64[64], ell_b64[64];
+    unsigned char output[32];
+    secp256k1_scalar rand_scalar;
+
+    testutil_random_scalar_order(&rand_scalar);
+    secp256k1_scalar_get_b32(s_good, &rand_scalar);
+
+    CHECK(secp256k1_ellswift_create(CTX, ell_a64, s_good, NULL) == 1);
+
+    testrand256_test(ell_b64);
+    testrand256_test(ell_b64 + 32);
+
+    memcpy(s_overflow_minus1, secp256k1_group_order_bytes, 32);
+    s_overflow_minus1[31] -= 1;
+    memcpy(s_overflow_plus1, secp256k1_group_order_bytes, 32);
+    s_overflow_plus1[31] += 1;
+    CHECK(secp256k1_ellswift_xdh(CTX, output, ell_a64, ell_b64, s_zero, 0, &ellswift_xdh_hash_x32, NULL) == 0);
+    CHECK(secp256k1_ellswift_xdh(CTX, output, ell_a64, ell_b64, secp256k1_group_order_bytes, 0, &ellswift_xdh_hash_x32, NULL) == 0);
+    CHECK(secp256k1_ellswift_xdh(CTX, output, ell_a64, ell_b64, s_overflow_plus1, 0, &ellswift_xdh_hash_x32, NULL) == 0);
+    CHECK(secp256k1_ellswift_xdh(CTX, output, ell_a64, ell_b64, s_overflow_minus1, 0, &ellswift_xdh_hash_x32, NULL) == 1);
+}
+
 /* --- Test registry --- */
 static const struct tf_test_entry tests_ellswift[] = {
     CASE1(ellswift_encoding_test_vectors_tests),
@@ -470,6 +497,7 @@ static const struct tf_test_entry tests_ellswift[] = {
     CASE1(ellswift_compute_shared_secret_tests),
     CASE1(ellswift_xdh_correctness_tests),
     CASE1(ellswift_hash_init_tests),
+    CASE1(ellswift_xdh_bad_scalar_tests),
 };
 
 #endif
```
