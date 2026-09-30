# [?] Prevent DenominatedAmount comparison from overflowing.

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2025-03-14
Source: https://github.com/namada-net/namada/commit/a74cd8a2518db24fde73ad72a039545354e7af59
Type: security-commit

## Details
Prevent DenominatedAmount comparison from overflowing.

## Patch
### crates/core/src/token.rs
```diff
@@ -671,10 +671,20 @@ impl PartialOrd for DenominatedAmount {
 
 impl Ord for DenominatedAmount {
     fn cmp(&self, other: &Self) -> Ordering {
-        if self.denom < other.denom {
+        if self.amount.is_zero() && other.is_zero() {
+            Ordering::Equal
+        } else if self.amount.is_zero() {
+            Ordering::Less
+        } else if other.amount.is_zero() {
+            Ordering::Greater
+        } else if self.denom < other.denom {
             // Cannot underflow cause `self.denom` < `other.denom`
             #[allow(clippy::arithmetic_side_effects)]
             let diff = other.denom.0 - self.denom.0;
+            if diff > 77 {
+                // This branch catches case where exponentiation overflows
+                return Ordering::Greater;
+            }
             let (div, rem) =
                 other.amount.raw.div_mod(Uint::exp10(diff as usize));
             let div_ceil = if rem.is_zero() {
@@ -696,6 +706,10 @@ impl Ord for DenominatedAmount {
             // Cannot underflow cause `other.denom` >= `self.denom`
             #[allow(clippy::arithmetic_side_effects)]
             let diff = self.denom.0 - other.denom.0;
+            if diff > 77 {
+                // This branch catches case where exponentiation overflows
+                return Ordering::Less;
+            }
             let (div, rem) =
                 self.amount.raw.div_mod(Uint::exp10(diff as usize));
             let div_ceil = if rem.is_zero() {
```
