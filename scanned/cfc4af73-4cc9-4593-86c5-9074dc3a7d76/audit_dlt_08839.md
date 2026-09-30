# [?] fix(corelib): Take::nth(usize::MAX) returns None instead of overflowing (#10022)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-06-01
Source: https://github.com/starkware-libs/cairo/commit/06a9b14b3b9f854af3eb6d45d81985b99cd8f867
Type: security-commit

## Details
fix(corelib): Take::nth(usize::MAX) returns None instead of overflowing (#10022)

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### corelib/src/iter/adapters/take.cairo
```diff
@@ -1,4 +1,4 @@
-use crate::num::traits::CheckedSub;
+use crate::num::traits::{CheckedAdd, CheckedSub};
 
 /// An iterator that only iterates over the first `n` iterations of `iter`.
 ///
@@ -29,7 +29,8 @@ impl TakeIterator<I, impl TIter: Iterator<I>, +Drop<I>> of Iterator<Take<I>> {
     fn nth<+Destruct<Take<I>>, +Destruct<Self::Item>>(
         ref self: Take<I>, n: usize,
     ) -> Option<Self::Item> {
-        if let Some(updated_n) = self.n.checked_sub(n + 1) {
+        if let Some(n_plus_1) = n.checked_add(1)
+            && let Some(updated_n) = self.n.checked_sub(n_plus_1) {
             self.n = updated_n;
             self.iter.nth(n)
         } else {
```

### corelib/src/test/iter_test.cairo
```diff
@@ -135,6 +135,10 @@ fn test_iter_adapter_take_nth() {
     // Test when n = 0
     let mut iter = (1_u8..=3).into_iter().take(0);
     assert_eq!(iter.nth(0), None);
+
+    // `nth(usize::MAX)` must return `None`, not overflow on `n + 1`.
+    let mut iter = (1_u8..=10).into_iter().take(5);
+    assert_eq!(iter.nth(core::num::traits::Bounded::<usize>::MAX), None);
 }
 
 #[test]
```
