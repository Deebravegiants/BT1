# [?] epee: fix array underflow in unicode parsing

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2020-04-23
Source: https://github.com/monero-project/monero/commit/3721d5688f7675c552f8da595f87f7af6c2ff114
Type: security-commit

## Details
epee: fix array underflow in unicode parsing

Reported by minerscan

Also independently found by OSS-Fuzz just recently

## Patch
### contrib/epee/include/storages/parserse_base_utils.h
```diff
@@ -196,7 +196,7 @@ namespace misc_utils
                 uint32_t dst = 0;
                 for (int i = 0; i < 4; ++i)
                 {
-                  const unsigned char tmp = isx[(int)*++it];
+                  const unsigned char tmp = isx[(unsigned char)*++it];
                   CHECK_AND_ASSERT_THROW_MES(tmp != 0xff, "Bad Unicode encoding");
                   dst = dst << 4 | tmp;
                 }
```
