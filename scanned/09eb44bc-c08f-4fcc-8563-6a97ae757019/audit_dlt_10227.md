# [?] TCT: fix Height docs, add overflow check

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2022-05-28
Source: https://github.com/penumbra-zone/penumbra/commit/cef92812b82d1099c2da93add34a34451e593f79
Type: security-commit

## Details
TCT: fix Height docs, add overflow check

## Patch
### tct/src/internal/height.rs
```diff
@@ -18,7 +18,7 @@ pub trait Height {
     type Height: Path;
 }
 
-/// The constant `u64` associated with each unary height.
+/// The constant `u8` associated with each unary height.
 pub trait IsHeight: sealed::IsHeight {
     /// The number for this height.
     const HEIGHT: u8;
@@ -35,7 +35,11 @@ impl IsHeight for Zero {
 pub struct Succ<N>(N);
 
 impl<N: IsHeight> IsHeight for Succ<N> {
-    const HEIGHT: u8 = N::HEIGHT + 1;
+    const HEIGHT: u8 = if let Some(n) = N::HEIGHT.checked_add(1) {
+        n
+    } else {
+        panic!("height overflow: can't construct something of height > u8::MAX")
+    };
 }
 
 /// Seal the `IsHeight` trait so that only `Succ` and `Zero` can inhabit it.
```
