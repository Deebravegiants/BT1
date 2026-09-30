# [?] fix: suppress intentional unsigned overflow in test/lcg.h

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-07-28
Source: https://github.com/dashpay/dash/commit/9ac20b8cf9913718eb2fb7c3c8d37abea915fdff
Type: security-commit

## Details
fix: suppress intentional unsigned overflow in test/lcg.h

  test/lcg.h:28       state = state * 6364136223846793005 + 1442695040888963407
                      an MMIX linear congruential generator; and it's meant to be
                      unsigned overflowed

## Patch
### test/sanitizer_suppressions/ubsan
```diff
@@ -45,6 +45,7 @@ unsigned-integer-overflow:coins.cpp
 unsigned-integer-overflow:compressor.cpp
 unsigned-integer-overflow:crypto/
 unsigned-integer-overflow:hash.cpp
+unsigned-integer-overflow:lcg.h
 unsigned-integer-overflow:policy/fees.cpp
 unsigned-integer-overflow:prevector.h
 unsigned-integer-overflow:EvalScript
```
