# [?] fix: suppress `float-cast-overflow` UBSan error from `qRound(double)`

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-02-09
Source: https://github.com/dashpay/dash/commit/1599cc69a4718d64ce04c463ac79a0cd529151c8
Type: security-commit

## Details
fix: suppress `float-cast-overflow` UBSan error from `qRound(double)`

## Patch
### test/sanitizer_suppressions/ubsan
```diff
@@ -100,3 +100,8 @@ shift-base:streams.h
 shift-base:test/fuzz/crypto_diff_fuzz_chacha20.cpp
 shift-base:util/bip32.cpp
 vptr:bls/bls.h
+
+# -fsanitize=float-cast-overflow suppressions
+# ===============================
+# See QTBUG-133261
+float-cast-overflow:qRound
```
