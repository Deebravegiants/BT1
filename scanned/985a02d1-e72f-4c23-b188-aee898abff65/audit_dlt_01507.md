# [?] cryptonote_basic: fix amount overflow detection on 32-bit systems

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2023-05-08
Source: https://github.com/monero-project/monero/commit/7206ef8ab85c921310ba45c1dd8b1621622aa696
Type: security-commit

## Details
cryptonote_basic: fix amount overflow detection on 32-bit systems

On systems where `ULONG_MAX` != `ULLONG_MAX` (e.g. most 32-bit systems), the `round_money_up` function will not correctly detect overflows.

## Patch
### src/cryptonote_basic/cryptonote_format_utils.cpp
```diff
@@ -1229,7 +1229,7 @@ namespace cryptonote
     char *end = NULL;
     errno = 0;
     const unsigned long long ull = strtoull(buf, &end, 10);
-    CHECK_AND_ASSERT_THROW_MES(ull != ULONG_MAX || errno == 0, "Failed to parse rounded amount: " << buf);
+    CHECK_AND_ASSERT_THROW_MES(ull != ULLONG_MAX || errno == 0, "Failed to parse rounded amount: " << buf);
     CHECK_AND_ASSERT_THROW_MES(ull != 0 || amount == 0, "Overflow in rounding");
     return ull;
   }
```
