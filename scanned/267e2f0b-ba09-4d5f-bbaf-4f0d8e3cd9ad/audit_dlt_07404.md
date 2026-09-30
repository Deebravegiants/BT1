# [?] fix(common): handle exponential precision overflow (#16731)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-09-08
Source: https://github.com/foundry-rs/foundry/commit/b8bb34701d2bdfdc07a7628e40e041dd15b903d7
Type: security-commit

## Details
fix(common): handle exponential precision overflow (#16731)

* fix(common): console.log %<n>e no longer panics on large precision

`console.log("%<n>e", value)` computed `10^n` via an unchecked/wrapping
pow with a user-controlled, unbounded `n`:

- U256: `Self::from(10).pow(Self::from(n))` wraps around on overflow
  instead of erroring. For n >= 256 the wrapped result is exactly 0
  (10 = 2*5, and 10^n has n factors of 2, which is >= 256 factors of 2
  once n >= 256), and the subsequent `amount / exp10` divides by that
  zero, panicking and aborting the entire `forge test` run.
- I256: `Self::exp10(n)` panics directly on overflow (n >= 77, since
  I256's positive range is one bit narrower than U256's).
- For 78 <= n <= 255 (U256), the wrapped `10^n` is nonzero garbage
  rather than exactly 0, so the format silently produces wrong digits
  instead of panicking.

Fixed by using `checked_pow` and handling the overflow case directly:
since `amount <= {U,I}256::MAX < 10^n` whenever `10^n` overflows, the
integer part is always 0 and the fractional part is `amount`'s own
digits left-padded to `n` digits. This fixes both the panic and the
wrong-digit range in one change - the two were the same root cause
(an unchecked pow) surfacing differently depending on exactly how far
past the type's capacity the wrap landed.

A `MAX_EXPONENTIAL_PRECISION` bound (1024) guards against an
absurdly large requested precision (still arbitrarily user-controlled)
producing an unbounded allocation; past it, the format falls back to
an explicit placeholder rather than silently truncating the padded
digits, which would misrepresent the value's magnitude.

Both `%<n>e` panics require no exotic value - a plain literal
precision in a format string is enough. Verified end-to-end with a
stash-and-rerun: the new regression test panics with the exact
reported error on unfixed code and passes after the fix.

* chore: add changelog entry for #16534

* chore: trim precision overflow comments

Shorten the added explanations while preserving the relevant invariants. Correct release metadata and recovery coverage where needed.

* fix(common): reject excessive precision

Treat excessive or overflowing exponential precision as an invalid format specifier, so it remains literal without consuming an argument. Share fixed-point rendering between signed and unsigned integers.

---------

Co-authored-by: gomes <17035424+gomesalexandre@users.noreply.github.com>
Co-authored-by: gomesalexandre <contact@alexandregomes.fr>

## Patch
### .changelog/pr-16534.md
```diff
@@ -0,0 +1,7 @@
+---
+foundry-common: patch
+foundry-common-fmt: patch
+forge: patch
+---
+
+Fixed console formatting panics and incorrect digits for large exponential precisions.
```

### crates/common/fmt/src/console.rs
```diff
@@ -3,6 +3,9 @@ use alloy_primitives::{Address, Bytes, FixedBytes, I256, U256};
 use comfy_table::{ContentLineStyle, LineStyle, Table, TableStyle};
 use std::fmt::{self, Write};
 
+/// Maximum accepted `%<n>e` precision.
+const MAX_EXPONENTIAL_PRECISION: usize = 1024;
+
 /// A piece is a portion of the format string which represents the next part to emit.
 #[derive(Clone, Debug, PartialEq, Eq)]
 pub enum Piece<'a> {
@@ -109,7 +112,10 @@ impl<'a> Parser<'a> {
             let n = self.integer(start);
             if let Some((_, 'e')) = self.peek() {
                 self.chars.next();
-                return Ok(FormatSpec::Exponential(n));
+                return n
+                    .filter(|&precision| precision <= MAX_EXPONENTIAL_PRECISION)
+                    .map(|precision| FormatSpec::Exponential(Some(precision)))
+                    .ok_or(ParseArgError::Err);
             }
         }
 
@@ -229,18 +235,7 @@ impl ConsoleFmt for U256 {
                     format!("{integer}.{decimal}e{log}")
                 }
             }
-            FormatSpec::Exponential(Some(precision)) => {
-                let exp10 = Self::from(10).pow(Self::from(precision));
-                let amount = *self;
-                let integer = amount / exp10;
-                let decimal = (amount % exp10).to_string();
-                let decimal = format!("{decimal:0>precision$}").trim_end_matches('0').to_string();
-                if decimal.is_empty() {
-                    format!("{integer}")
-                } else {
-                    format!("{integer}.{decimal}")
-                }
-            }
+            FormatSpec::Exponential(Some(precision)) => format_fixed(*self, "", precision),
         }
     }
 }
@@ -276,20 +271,25 @@ impl ConsoleFmt for I256 {
             FormatSpec::Exponential(Some(precision)) => {
                 let amount = *self;
                 let sign = if amount.is_negative() { "-" } else { "" };
-                let exp10 = Self::exp10(precision);
-                let integer = (amount / exp10).twos_complement();
-                let decimal = (amount % exp10).twos_complement().to_string();
-                let decimal = format!("{decimal:0>precision$}").trim_end_matches('0').to_string();
-                if decimal.is_empty() {
-                    format!("{sign}{integer}")
-                } else {
-                    format!("{sign}{integer}.{decimal}")
-                }
+                format_fixed(amount.unsigned_abs(), sign, precision)
             }
         }
     }
 }
 
+fn format_fixed(amount: U256, sign: &str, precision: usize) -> String {
+    let (integer, decimal) = U256::from(10)
+        .checked_pow(U256::from(precision))
+        .map_or((U256::ZERO, amount), |exp10| (amount / exp10, amount % exp10));
+    let decimal = decimal.to_string();
+    let decimal = format!("{decimal:0>precision$}").trim_end_matches('0').to_string();
+    if decimal.is_empty() {
+        format!("{sign}{integer}")
+    } else {
+        format!("{sign}{integer}.{decimal}")
+    }
+}
+
 impl ConsoleFmt for Address {
     fn fmt(&self, spec: FormatSpec) -> String {
         match spec {
@@ -593,6 +593,53 @@ mod tests {
         );
     }
 
+    // Overflow used to panic or silently produce incorrect digits.
+    #[test]
+    fn test_console_log_exponential_precision_overflow() {
+        let fmt_1 = |spec: &str, arg: &dyn ConsoleFmt| console_format(spec, &[arg]);
+
+        // 10^256 wraps to zero with unchecked exponentiation.
+        assert_eq!(format!("0.{}1", "0".repeat(255)), fmt_1("%256e", &U256::from(1)));
+
+        // 10^78 overflows U256; 10^77 still fits.
+        let ten_pow_77 = U256::from(10).pow(U256::from(77u64));
+        assert_eq!("0.1", fmt_1("%78e", &ten_pow_77));
+
+        assert_eq!("1", fmt_1("%77e", &ten_pow_77));
+
+        // 10^77 exceeds I256::MAX.
+        assert_eq!(format!("0.{}1", "0".repeat(76)), fmt_1("%77e", &I256::try_from(1).unwrap()));
+        assert_eq!(format!("-0.{}1", "0".repeat(76)), fmt_1("%77e", &I256::try_from(-1).unwrap()));
+
+        // Preserve the value at the maximum accepted precision.
+        assert_eq!(format!("0.{}1", "0".repeat(1023)), fmt_1("%1024e", &U256::from(1)));
+
+        // Invalid precisions remain literal and do not consume the value.
+        assert_eq!("%1025e 1", fmt_1("%1025e", &U256::from(1)));
+        assert_eq!("%99999999999999999999e 1", fmt_1("%99999999999999999999e", &U256::from(1)));
+
+        assert_eq!("1", fmt_1("%18e", &U256::from(1_000_000_000_000_000_000u64)));
+
+        assert_eq!("0", fmt_1("%0e", &U256::from(0)));
+        assert_eq!("0", fmt_1("%256e", &U256::from(0)));
+
+        // Check signed and unsigned extrema at their overflow boundaries.
+        let expect_fallback = |digits: String, precision: usize, sign: &str| {
+            let padded = format!("{digits:0>precision$}");
+            let trimmed = padded.trim_end_matches('0');
+            if trimmed.is_empty() { format!("{sign}0") } else { format!("{sign}0.{trimmed}") }
+        };
+        assert_eq!(expect_fallback(U256::MAX.to_string(), 78, ""), fmt_1("%78e", &U256::MAX));
+        assert_eq!(
+            expect_fallback(I256::MIN.unsigned_abs().to_string(), 77, "-"),
+            fmt_1("%77e", &I256::MIN)
+        );
+        assert_eq!(
+            expect_fallback(I256::MAX.unsigned_abs().to_string(), 77, ""),
+            fmt_1("%77e", &I256::MAX)
+        );
+    }
+
     #[test]
     fn test_console_log_format() {
         let mut log1 = Log1 { p_0: "foo %s".to_string(), p_1: U256::from(100) };
```
