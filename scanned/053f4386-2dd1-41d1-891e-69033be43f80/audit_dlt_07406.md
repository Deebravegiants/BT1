# [?] fix(cast): reject a decimals/len argument too large to safely format, instead of panicking (#16577)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-09-04
Source: https://github.com/foundry-rs/foundry/commit/364468432a39646f4b47e4ce3bcfbc6d03fb75a4
Type: security-commit

## Details
fix(cast): reject a decimals/len argument too large to safely format, instead of panicking (#16577)

* fix(cast): reject a decimals/len argument too large to safely format, instead of panicking

cast to-fixed-point and cast pad both build their output via a dynamic
format! width - decimals for to-fixed-point, len * 2 for pad. Rust's
dynamic format width panics with 'Formatting argument out of range'
above u16::MAX (verified: width 65535 formats fine, 65536 panics).

to-fixed-point had a second, more severe issue: decimals is parsed as
a U256 then converted via .to::<usize>(), which panics outright
('Uint conversion error: Overflow') on any value that doesn't fit in a
usize at all - e.g. cast to-fixed-point 18446744073709551616 10 passes
decimals=18446744073709551616 (2^64, per this command's actual
positional order: <decimals> <value>), which overflows a 64-bit usize
before the format-width panic would even be reached.

Live repros, all previously panicking:
  cast to-fixed-point 18446744073709551616 10   (decimals overflows usize)
  cast to-fixed-point 70000 12345               (decimals exceeds format width limit)
  cast pad --len 32768 abcd                     (len * 2 exceeds format width limit)

Fix: validate decimals/len against both the fallible integer
conversion and the u16::MAX format-width ceiling up front, returning a
clean error instead of panicking either way. pad's len * 2
multiplication is also now checked rather than able to silently wrap.

Added regression tests for all three cases plus the valid boundary.
Existing doctests for both functions still pass unchanged.

closes nothing - filed independently, no corresponding issue was open.

* chore(cast): address review feedback

* Update crates/cast/src/lib.rs

* Update crates/cast/src/lib.rs

---------

Co-authored-by: steven <corderosteven6@gmail.com>
Co-authored-by: Mablr <59505383+mablr@users.noreply.github.com>
Co-authored-by: stevencartavia <112043913+stevencartavia@users.noreply.github.com>
Co-authored-by: figtracer <me@figtracer.com>

## Patch
### .changelog/reject-oversized-cast-format-widths.md
```diff
@@ -0,0 +1,5 @@
+---
+cast: patch
+---
+
+Return errors from `cast to-fixed-point` and `cast pad` when their requested output width is too large.
```

### crates/cast/src/lib.rs
```diff
@@ -1458,7 +1458,12 @@ impl SimpleCast {
             let value_len = value_stripped.len();
             (sign, value_stripped, value_len)
         };
-        let decimals = NumberWithBase::parse_uint(decimals, None)?.number().to::<usize>();
+        let decimals_num = NumberWithBase::parse_uint(decimals, None)?.number();
+        let decimals: usize = decimals_num
+            .try_into()
+            .ok()
+            .filter(|&d: &usize| d <= u16::MAX as usize)
+            .ok_or_else(|| eyre::eyre!("decimals out of range: {decimals_num}"))?;
 
         let value = if decimals >= value_len {
             // Add "0." and pad with 0s
@@ -1863,7 +1868,10 @@ impl SimpleCast {
     /// ```
     pub fn pad(s: &str, right: bool, len: usize) -> Result<String> {
         let s = strip_0x(s);
-        let hex_len = len * 2;
+        let hex_len = len
+            .checked_mul(2)
+            .filter(|&h| h <= u16::MAX as usize)
+            .ok_or_else(|| eyre::eyre!("len out of range: {len}"))?;
 
         // Validate input
         if s.len() > hex_len {
@@ -3047,4 +3055,30 @@ mod tests {
             "00000000: PUSH32 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff\n"
         );
     }
+
+    #[test]
+    fn to_fixed_point_rejects_decimals_too_large_to_convert() {
+        assert!(Cast::to_fixed_point("10", "18446744073709551616").is_err());
+    }
+
+    #[test]
+    fn to_fixed_point_rejects_decimals_above_format_width_limit() {
+        assert!(Cast::to_fixed_point("12345", "70000").is_err());
+        assert!(Cast::to_fixed_point("12345", "65536").is_err());
+    }
+
+    #[test]
+    fn pad_rejects_len_above_format_width_limit() {
+        assert!(Cast::pad("abcd", false, 32768).is_err());
+        assert!(Cast::pad("abcd", false, usize::MAX).is_err());
+    }
+
+    #[test]
+    fn pad_and_to_fixed_point_still_work_for_valid_inputs() {
+        assert_eq!(
+            Cast::pad("abcd", false, 20).unwrap(),
+            "0x000000000000000000000000000000000000abcd"
+        );
+        assert_eq!(Cast::to_fixed_point("10", "2").unwrap(), "0.10");
+    }
 }
```
