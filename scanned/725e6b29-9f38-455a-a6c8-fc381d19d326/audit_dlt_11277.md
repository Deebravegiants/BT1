# [?] fix: check overflow for Pedersen grumpkin scalars (#10462)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-11-11
Source: https://github.com/noir-lang/noir/commit/975ef74029c784e2df96e05fe3bac27593b3d111
Type: security-commit

## Details
fix: check overflow for Pedersen grumpkin scalars (#10462)

## Patch
### noir_stdlib/src/field/bn254.nr
```diff
@@ -2,8 +2,8 @@ use crate::field::field_less_than;
 use crate::runtime::is_unconstrained;
 
 // The low and high decomposition of the field modulus
-global PLO: Field = 53438638232309528389504892708671455233;
-global PHI: Field = 64323764613183177041862057485226039389;
+pub(crate) global PLO: Field = 53438638232309528389504892708671455233;
+pub(crate) global PHI: Field = 64323764613183177041862057485226039389;
 
 pub(crate) global TWO_POW_128: Field = 0x100000000000000000000000000000000;
 
```

### noir_stdlib/src/hash/mod.nr
```diff
@@ -114,14 +114,23 @@ fn __derive_generators<let N: u32, let M: u32>(
 ) -> [EmbeddedCurvePoint; N] {}
 
 #[field(bn254)]
-// Same as from_field but:
-// does not assert the limbs are 128 bits
-// does not assert the decomposition does not overflow the EmbeddedCurveScalar
+// Decompose the input 'bn254 scalar' into two 128 bits limbs.
+// It is called 'unsafe' because it does not assert the limbs are 128 bits
+// Assuming the limbs are 128 bits:
+// Assert the decomposition does not overflow the field size.
 fn from_field_unsafe(scalar: Field) -> EmbeddedCurveScalar {
     // Safety: xlo and xhi decomposition is checked below
     let (xlo, xhi) = unsafe { crate::field::bn254::decompose_hint(scalar) };
     // Check that the decomposition is correct
     assert_eq(scalar, xlo + crate::field::bn254::TWO_POW_128 * xhi);
+    // Check that the decomposition does not overflow the field size
+    let (a, b) = if xhi == crate::field::bn254::PHI {
+        (xlo, crate::field::bn254::PLO)
+    } else {
+        (xhi, crate::field::bn254::PHI)
+    };
+    crate::field::bn254::assert_lt(a, b);
+
     EmbeddedCurveScalar { lo: xlo, hi: xhi }
 }
 
```

### tooling/nargo_cli/tests/snapshots/compile_success_empty/arithmetic_generics/execute__tests__expanded.snap
```diff
@@ -24,8 +24,8 @@ fn split_first<T, let N: u32>(array: [T; N]) -> (T, [T; N - 1]) {
 fn push<let N: u32>(array: [Field; N], element: Field) -> [Field; N + 1] {
     let mut result: [Field; N + 1] = std::mem::zeroed();
     {
-        let i_4524: u32 = array.len();
-        result[i_4524] = element;
+        let i_4526: u32 = array.len();
+        result[i_4526] = element;
     };
     for i in 0_u32..array.len() {
         result[i] = array[i];
```

### tooling/nargo_cli/tests/snapshots/compile_success_empty/assign_mutation_in_lvalue/execute__tests__expanded.snap
```diff
@@ -10,11 +10,11 @@ fn main() {
 fn bug() {
     let mut a: ([Field; 2], Field) = ([1_Field, 2_Field], 3_Field);
     {
-        let i_4493: u32 = {
+        let i_4495: u32 = {
             a = ([4_Field, 5_Field], 6_Field);
             1_u32
         };
-        a.0[i_4493] = 7_Field;
+        a.0[i_4495] = 7_Field;
     };
     assert(a == ([4_Field, 7_Field], 6_Field));
 }
```

### tooling/nargo_cli/tests/snapshots/compile_success_empty/numeric_generics/execute__tests__expanded.snap
```diff
@@ -27,8 +27,8 @@ impl<let S: u32> MyStruct<S> {
     fn insert(mut self, index: Field, elem: Field) -> Self {
         assert((index as u64) < (S as u64));
         {
-            let i_4507: u32 = index as u32;
-            self.data[i_4507] = elem;
+            let i_4509: u32 = index as u32;
+            self.data[i_4509] = elem;
         };
         self
     }
```

### tooling/nargo_cli/tests/snapshots/compile_success_empty/numeric_generics_explicit/execute__tests__expanded.snap
```diff
@@ -36,8 +36,8 @@ impl<let S: u32> MyStruct<S> {
     fn insert(mut self, index: Field, elem: Field) -> Self {
         assert((index as u32) < S);
         {
-            let i_4522: u32 = index as u32;
-            self.data[i_4522] = elem;
+            let i_4524: u32 = index as u32;
+            self.data[i_4524] = elem;
         };
         self
     }
```

### tooling/nargo_cli/tests/snapshots/compile_success_empty/regression_bignum/execute__tests__expanded.snap
```diff
@@ -53,8 +53,8 @@ unconstrained fn shl(shift: u32) -> [u64; 6] {
     result[num_shifted_limbs] = 1_u64 << limb_shift;
     for i in 1_u32..6_u32 - num_shifted_limbs {
         {
-            let i_4514: u32 = i + num_shifted_limbs;
-            result[i_4514] = 0_u64;
+            let i_4516: u32 = i + num_shifted_limbs;
+            result[i_4516] = 0_u64;
         }
     }
     result
```

### tooling/nargo_cli/tests/snapshots/compile_success_empty/serialize_1/execute__tests__expanded.snap
```diff
@@ -25,8 +25,8 @@ where
         }
         for i in 0_u32..b.len() {
             {
-                let i_4516: u32 = i + a.len();
-                array[i_4516] = b[i];
+                let i_4518: u32 = i + a.len();
+                array[i_4518] = b[i];
             }
         }
         array
```

### tooling/nargo_cli/tests/snapshots/compile_success_empty/serialize_4/execute__tests__expanded.snap
```diff
@@ -25,8 +25,8 @@ where
         }
         for i in 0_u32..b.len() {
             {
-                let i_4516: u32 = i + a.len();
-                array[i_4516] = b[i];
+                let i_4518: u32 = i + a.len();
+                array[i_4518] = b[i];
             }
         }
         array
```

### tooling/nargo_cli/tests/snapshots/compile_success_no_bug/ram_blowup_regression/execute__tests__expanded.snap
```diff
@@ -29,8 +29,8 @@ fn main(tx_effects_hash_input: [Field; 256]) -> pub Field {
         let input_as_bytes: [u8; 32] = tx_effects_hash_input[offset].to_be_bytes();
         for byte_index in 0_u32..32_u32 {
             {
-                let i_4508: u32 = (offset * 32_u32) + byte_index;
-                hash_input_flattened[i_4508] = input_as_bytes[byte_index];
+                let i_4510: u32 = (offset * 32_u32) + byte_index;
+                hash_input_flattened[i_4510] = input_as_bytes[byte_index];
             }
         }
     }
```

### tooling/nargo_cli/tests/snapshots/execution_success/aes128_encrypt/execute__tests__expanded.snap
```diff
@@ -18,8 +18,8 @@ unconstrained fn decode_hex<let N: u32, let M: u32>(s: str<N>) -> [u8; M] {
     for i in 0_u32..N {
         if (i % 2_u32) != 0_u32 { continue; };
         {
-            let i_4508: u32 = i / 2_u32;
-            result[i_4508] =
+            let i_4510: u32 = i / 2_u32;
+            result[i_4510] =
                 (decode_ascii(as_bytes[i]) * 16_u8) + decode_ascii(as_bytes[i + 1_u32]);
         }
     }
```

### tooling/nargo_cli/tests/snapshots/execution_success/array_dedup_regression/execute__tests__expanded.snap
```diff
@@ -7,8 +7,8 @@ unconstrained fn main(x: u32) {
     for i in 0_u32..5_u32 {
         let mut a2: [Field; 5] = [1_Field, 2_Field, 3_Field, 4_Field, 5_Field];
         {
-            let i_4495: u32 = x + i;
-            a2[i_4495] = 128_Field;
+            let i_4497: u32 = x + i;
+            a2[i_4497] = 128_Field;
         };
         println(a2);
         if i != 0_u32 {
```
