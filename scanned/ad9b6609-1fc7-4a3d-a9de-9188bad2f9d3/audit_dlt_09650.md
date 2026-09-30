# [?] Avoid integer overflows in scriptnum tests

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2017-01-10
Source: https://github.com/dogecoin/dogecoin/commit/f94f3e0df82cd9f1202b0741c6fcc83b3560cee8
Type: security-commit

## Details
Avoid integer overflows in scriptnum tests

## Patch
### src/test/scriptnum_tests.cpp
```diff
@@ -12,8 +12,10 @@
 
 BOOST_FIXTURE_TEST_SUITE(scriptnum_tests, BasicTestingSetup)
 
-static const int64_t values[] = \
-{ 0, 1, CHAR_MIN, CHAR_MAX, UCHAR_MAX, SHRT_MIN, USHRT_MAX, INT_MIN, INT_MAX, UINT_MAX, LONG_MIN, LONG_MAX };
+/** A selection of numbers that do not trigger int64_t overflow
+ *  when added/subtracted. */
+static const int64_t values[] = { 0, 1, -2, 127, 128, -255, 256, (1LL << 15) - 1, -(1LL << 16), (1LL << 24) - 1, (1LL << 31), 1 - (1LL << 32), 1LL << 40 };
+
 static const int64_t offsets[] = { 1, 0x79, 0x80, 0x81, 0xFF, 0x7FFF, 0x8000, 0xFFFF, 0x10000};
 
 static bool verify(const CScriptNum10& bignum, const CScriptNum& scriptnum)
```
