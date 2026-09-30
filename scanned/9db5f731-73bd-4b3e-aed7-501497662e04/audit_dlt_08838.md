# [?] bugfix(corelib): Fixed ByteSpan::get OOB empty range. (#10051)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-06-07
Source: https://github.com/starkware-libs/cairo/commit/20fb35b1878a586b055621ba729975f02fa27431
Type: security-commit

## Details
bugfix(corelib): Fixed ByteSpan::get OOB empty range. (#10051)

## Patch
### corelib/src/byte_array.cairo
```diff
@@ -859,7 +859,13 @@ impl ByteSpanGetRange of crate::ops::Get<ByteSpan, crate::ops::Range<usize>> {
     fn get(self: @ByteSpan, index: crate::ops::Range<usize>) -> Option<ByteSpan> {
         let range = index;
         if range.start == range.end {
-            return Some(Default::default());
+            return if range.start <= (*self).len() {
+                // If range is within bounds, return the empty slice.
+                Some(Default::default())
+            } else {
+                // If range is out of bounds, return `None`.
+                None
+            };
         }
         if range.start > range.end {
             return None;
```

### corelib/src/test/byte_array_test.cairo
```diff
@@ -550,15 +550,25 @@ fn test_span_slice_is_empty() {
     assert!(empty.is_empty());
     assert_eq!(empty.to_byte_array(), "");
 
+    assert_eq!(span.get(5..5).map(is_empty), Some(true));
+    assert_eq!(span.get(6..6).map(is_empty), None);
+    assert_eq!(span.get(2..6).map(is_empty), None);
+    assert_eq!(span.get(0..10).map(is_empty), None);
+
     let ba_31: ByteArray = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcde";
     assert_eq!(ba_31.span().get(30..30).map(is_empty), Some(true));
     assert_eq!(ba_31.span().get(31..31).map(is_empty), Some(true));
     assert_eq!(ba_31.span().get(15..30).map(is_empty), Some(false));
+    assert_eq!(ba_31.span().get(32..32).map(is_empty), None);
+    assert_eq!(ba_31.span().get(15..32).map(is_empty), None);
+    assert_eq!(ba_31.span().get(0..70).map(is_empty), None);
 
     let ba_30: ByteArray = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcd";
     assert_eq!(ba_30.span().get(29..29).map(is_empty), Some(true));
     assert_eq!(ba_30.span().get(30..30).map(is_empty), Some(true));
     assert_eq!(ba_30.span().get(15..29).map(is_empty), Some(false));
+    assert_eq!(ba_30.span().get(31..31).map(is_empty), None);
+    assert_eq!(ba_30.span().get(15..31).map(is_empty), None);
 }
 
 #[test]
```
