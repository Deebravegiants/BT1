# [?] Fix Array Deserialization Panic (#837)

## Summary
Severity: Unknown
Chain: ZK
Component: arkworks-rs/algebra
Published: 2024-06-19
Source: https://github.com/arkworks-rs/algebra/commit/79a5fe3f0e17ecec7aa683fa58dd02e14eb28a8b
Type: security-commit

## Details
Fix Array Deserialization Panic (#837)

* Fix Array Deserialization Panic

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* Amend CHANGELOG

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* Use ArrayVec instead of unsafe

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* Unrelated fmt

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* Defensive programming not needed

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* .ok().unwrap()

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

---------

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>
Co-authored-by: Pratyush Mishra <pratyushmishra@berkeley.edu>

## Patch
### CHANGELOG.md
```diff
@@ -4,6 +4,7 @@
 
 - [\#772](https://github.com/arkworks-rs/algebra/pull/772) (`ark-ff`) Implementation of `mul` method for `BigInteger`.
 - [\#794](https://github.com/arkworks-rs/algebra/pull/794) (`ark-ff`) Fix `wasm` compilation.
+- [\#837](https://github.com/arkworks-rs/algebra/pull/837) (`ark-serialize`) Fix array deserialization panic.
 
 ### Breaking changes
 
```

### Cargo.toml
```diff
@@ -52,6 +52,7 @@ num-traits = { version = "0.2", default-features = false }
 num-bigint = { version = "0.4", default-features = false }
 num-integer = { version = "0.1", default-features = false }
 
+arrayvec = { version = "0.7", default-features = false }
 criterion = "0.5.0"
 educe = "0.5.0"
 digest = { version = "0.10", default-features = false }
```

### ff/Cargo.toml
```diff
@@ -20,7 +20,7 @@ ark-ff-asm.workspace = true
 ark-ff-macros.workspace = true
 ark-std.workspace = true
 ark-serialize.workspace = true
-arrayvec = { version = "0.7", default-features = false }
+arrayvec.workspace = true
 educe.workspace = true
 num-traits.workspace = true
 paste.workspace = true
```

### serialize/Cargo.toml
```diff
@@ -18,6 +18,7 @@ keywords = ["cryptography", "serialization" ]
 [dependencies]
 ark-serialize-derive = { workspace = true, optional = true }
 ark-std.workspace = true
+arrayvec.workspace = true
 digest.workspace = true
 num-bigint.workspace = true
 rayon = { workspace = true, optional = true }
```

### serialize/src/impls.rs
```diff
@@ -10,6 +10,7 @@ use ark_std::{
     string::*,
     vec::*,
 };
+use arrayvec::ArrayVec;
 use num_bigint::BigUint;
 
 impl Valid for bool {
@@ -458,13 +459,18 @@ impl<T: CanonicalDeserialize, const N: usize> CanonicalDeserialize for [T; N] {
         compress: Compress,
         validate: Validate,
     ) -> Result<Self, SerializationError> {
-        let result = core::array::from_fn(|_| {
-            T::deserialize_with_mode(&mut reader, compress, Validate::No).unwrap()
-        });
+        let mut array = ArrayVec::<T, N>::new();
+        for _ in 0..N {
+            array.push(T::deserialize_with_mode(
+                &mut reader,
+                compress,
+                Validate::No,
+            )?);
+        }
         if let Validate::Yes = validate {
-            T::batch_check(result.iter())?
+            T::batch_check(array.iter())?
         }
-        Ok(result)
+        Ok(array.into_inner().ok().unwrap())
     }
 }
 
```

### serialize/src/test.rs
```diff
@@ -126,6 +126,13 @@ fn test_array() {
     test_serialize([1u8; 33]);
 }
 
+#[test]
+fn test_array_bad_input() {
+    // Does not panic on invalid data:
+    let serialized = vec![0u8; 1];
+    assert!(<[u8; 2]>::deserialize_compressed(&serialized[..]).is_err());
+}
+
 #[test]
 fn test_vec() {
     test_serialize(vec![1u64, 2, 3, 4, 5]);
```
