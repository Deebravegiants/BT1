# [?] fix(core/ui): avoid signed overflow when calculating text width

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-06-02
Source: https://github.com/trezor/trezor-firmware/commit/7c429403859a5772a80c75dd603510830fec931e
Type: security-commit

## Details
fix(core/ui): avoid signed overflow when calculating text width

[no changelog]

## Patch
### core/embed/rust/src/ui/display/font.rs
```diff
@@ -1,3 +1,5 @@
+use core::num::Saturating;
+
 #[cfg(feature = "translations")]
 use spin::RwLockReadGuard;
 
@@ -242,15 +244,17 @@ fn calculate_glyph_size(header: &[u8]) -> usize {
 impl FontInfo {
     /// Supports UTF8 characters
     pub fn text_width(&'static self, text: &str) -> i16 {
-        let mut width = 0;
+        // Really long text makes width overflow into negative values.
+        // It's better to return i16::MAX in that case.
+        let mut width = Saturating(0);
         let mut prev_char: Option<char> = None;
 
         for c in text.chars() {
             width += prev_char.map_or(0, |left| i16::from(self.get_kerning(left, c)));
             width += self.char_width(c);
             prev_char = Some(c);
         }
-        width
+        width.0
     }
 
     /// Width of the text that is visible.
```
