# [?] masp: fix possible underflow

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2023-11-29
Source: https://github.com/namada-net/namada/commit/b41393ea59634eb199949e77c29052d7f571c0f2
Type: security-commit

## Details
masp: fix possible underflow

## Patch
### core/src/ledger/masp_conversions.rs
```diff
@@ -344,7 +344,8 @@ where
                     total_reward += (addr_bal
                         * (new_normed_inflation, *normed_inflation))
                         .0
-                        - addr_bal;
+                        .checked_sub(addr_bal)
+                        .unwrap_or_default();
                     // Save the new normed inflation
                     *normed_inflation = new_normed_inflation;
                 }
```
