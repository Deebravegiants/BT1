# [?] runtime: avoid panic on mismatching length

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2022-08-05
Source: https://github.com/graphprotocol/graph-node/commit/8b5fcd10f22ec60b443f50e6f438ab2418baa4ec
Type: security-commit

## Details
runtime: avoid panic on mismatching length

## Patch
### runtime/wasm/src/to_from/mod.rs
```diff
@@ -1,3 +1,4 @@
+use anyhow::anyhow;
 use std::collections::HashMap;
 use std::hash::Hash;
 use std::iter::FromIterator;
@@ -33,15 +34,15 @@ impl<T: AscValue> FromAscObj<TypedArray<T>> for Vec<T> {
     }
 }
 
-impl<T: AscValue, const LEN: usize> FromAscObj<TypedArray<T>> for [T; LEN] {
+impl<T: AscValue + Send + Sync, const LEN: usize> FromAscObj<TypedArray<T>> for [T; LEN] {
     fn from_asc_obj<H: AscHeap + ?Sized>(
         typed_array: TypedArray<T>,
         heap: &H,
         gas: &GasCounter,
     ) -> Result<Self, DeterministicHostError> {
-        let mut array: [T; LEN] = [T::default(); LEN];
         let v = typed_array.to_vec(heap, gas)?;
-        array.copy_from_slice(&v);
+        let array = <[T; LEN]>::try_from(v)
+            .map_err(|v| anyhow!("expected array of length {}, found length {}", LEN, v.len()))?;
         Ok(array)
     }
 }
```
