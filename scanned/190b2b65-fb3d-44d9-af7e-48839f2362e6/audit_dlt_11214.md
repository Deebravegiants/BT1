# [?] fix overflows in to_lookup_operands

## Summary
Severity: Unknown
Chain: ZK
Component: a16z/jolt
Published: 2025-08-04
Source: https://github.com/a16z/jolt/commit/58f372e94f054d4fcca39e35abdc294bbf450265
Type: security-commit

## Details
fix overflows in to_lookup_operands

Signed-off-by: Andrew Tretyakov <42178850+0xAndoroid@users.noreply.github.com>

## Patch
### jolt-core/src/zkvm/instruction/add.rs
```diff
@@ -29,7 +29,7 @@ impl InstructionFlags for ADD {
 impl<const WORD_SIZE: usize> LookupQuery<WORD_SIZE> for RISCVCycle<ADD> {
     fn to_lookup_operands(&self) -> (u64, u128) {
         let (x, y) = LookupQuery::<WORD_SIZE>::to_instruction_inputs(self);
-        (0, x as u128 + y as u128)
+        (0, x as u128 + y as u64 as u128)
     }
 
     fn to_lookup_index(&self) -> u128 {
```

### jolt-core/src/zkvm/instruction/addi.rs
```diff
@@ -29,7 +29,7 @@ impl InstructionFlags for ADDI {
 impl<const WORD_SIZE: usize> LookupQuery<WORD_SIZE> for RISCVCycle<ADDI> {
     fn to_lookup_operands(&self) -> (u64, u128) {
         let (x, y) = LookupQuery::<WORD_SIZE>::to_instruction_inputs(self);
-        (0, x as u128 + y as u128)
+        (0, x as u128 + y as u64 as u128)
     }
 
     fn to_lookup_index(&self) -> u128 {
```

### jolt-core/src/zkvm/instruction/mul.rs
```diff
@@ -29,7 +29,7 @@ impl InstructionFlags for MUL {
 impl<const WORD_SIZE: usize> LookupQuery<WORD_SIZE> for RISCVCycle<MUL> {
     fn to_lookup_operands(&self) -> (u64, u128) {
         let (x, y) = LookupQuery::<WORD_SIZE>::to_instruction_inputs(self);
-        (0, x as u128 * y as u128)
+        (0, x as u128 * y as u64 as u128)
     }
 
     fn to_lookup_index(&self) -> u128 {
```

### jolt-core/src/zkvm/instruction/mulhu.rs
```diff
@@ -29,7 +29,7 @@ impl InstructionFlags for MULHU {
 impl<const WORD_SIZE: usize> LookupQuery<WORD_SIZE> for RISCVCycle<MULHU> {
     fn to_lookup_operands(&self) -> (u64, u128) {
         let (x, y) = LookupQuery::<WORD_SIZE>::to_instruction_inputs(self);
-        (0, (x as u128) * (y as u128))
+        (0, x as u128 * y as u64 as u128)
     }
 
     fn to_lookup_index(&self) -> u128 {
@@ -58,7 +58,7 @@ impl<const WORD_SIZE: usize> LookupQuery<WORD_SIZE> for RISCVCycle<MULHU> {
             #[cfg(test)]
             8 => (x * y as u64) >> 8,
             32 => (x * y as u64) >> 32,
-            64 => ((x as u128).wrapping_mul(y as u128) >> 64) as u64,
+            64 => (((x as u128) * (y as u64 as u128)) >> 64) as u64,
             _ => panic!("{WORD_SIZE}-bit word size is unsupported"),
         }
     }
```

### jolt-core/src/zkvm/instruction/virtual_extend.rs
```diff
@@ -28,7 +28,7 @@ impl InstructionFlags for VirtualExtend {
 impl<const WORD_SIZE: usize> LookupQuery<WORD_SIZE> for RISCVCycle<VirtualExtend> {
     fn to_lookup_operands(&self) -> (u64, u128) {
         let (x, y) = LookupQuery::<WORD_SIZE>::to_instruction_inputs(self);
-        (0, x as u128 + y as u128)
+        (0, u128::try_from(x as i128 + y as i128).unwrap())
     }
 
     fn to_instruction_inputs(&self) -> (u64, i64) {
```

### jolt-core/src/zkvm/instruction/virtual_muli.rs
```diff
@@ -30,7 +30,7 @@ impl InstructionFlags for VirtualMULI {
 impl<const WORD_SIZE: usize> LookupQuery<WORD_SIZE> for RISCVCycle<VirtualMULI> {
     fn to_lookup_operands(&self) -> (u64, u128) {
         let (x, y) = LookupQuery::<WORD_SIZE>::to_instruction_inputs(self);
-        (0, (x as u128) * (y as u128))
+        (0, x as u128 * y as u64 as u128)
     }
 
     fn to_lookup_index(&self) -> u128 {
```

### jolt-core/src/zkvm/instruction/virtual_pow2.rs
```diff
@@ -39,7 +39,7 @@ impl<const WORD_SIZE: usize> LookupQuery<WORD_SIZE> for RISCVCycle<VirtualPow2>
 
     fn to_lookup_operands(&self) -> (u64, u128) {
         let (x, y) = LookupQuery::<WORD_SIZE>::to_instruction_inputs(self);
-        (0, x as u128 + y as u128)
+        (0, x as u128 + y as u64 as u128)
     }
 
     fn to_lookup_index(&self) -> u128 {
```

### jolt-core/src/zkvm/instruction/virtual_pow2i.rs
```diff
@@ -38,7 +38,7 @@ impl<const WORD_SIZE: usize> LookupQuery<WORD_SIZE> for RISCVCycle<VirtualPow2I>
 
     fn to_lookup_operands(&self) -> (u64, u128) {
         let (x, y) = LookupQuery::<WORD_SIZE>::to_instruction_inputs(self);
-        (0, x as u128 + y as u128)
+        (0, x as u128 + y as u64 as u128)
     }
 
     fn to_lookup_index(&self) -> u128 {
```

### jolt-core/src/zkvm/instruction/virtual_pow2iw.rs
```diff
@@ -33,7 +33,7 @@ impl<const WORD_SIZE: usize> LookupQuery<WORD_SIZE> for RISCVCycle<VirtualPow2IW
 
     fn to_lookup_operands(&self) -> (u64, u128) {
         let (x, y) = LookupQuery::<WORD_SIZE>::to_instruction_inputs(self);
-        (0, x as u128 + y as u128)
+        (0, x as u128 + y as u64 as u128)
     }
 
     fn to_lookup_index(&self) -> u128 {
```

### jolt-core/src/zkvm/instruction/virtual_pow2w.rs
```diff
@@ -34,7 +34,7 @@ impl<const WORD_SIZE: usize> LookupQuery<WORD_SIZE> for RISCVCycle<VirtualPow2W>
 
     fn to_lookup_operands(&self) -> (u64, u128) {
         let (x, y) = LookupQuery::<WORD_SIZE>::to_instruction_inputs(self);
-        (0, x as u128 + y as u128)
+        (0, x as u128 + y as u64 as u128)
     }
 
     fn to_lookup_index(&self) -> u128 {
```

### jolt-core/src/zkvm/instruction/virtual_shift_right_bitmask.rs
```diff
@@ -39,7 +39,7 @@ impl<const WORD_SIZE: usize> LookupQuery<WORD_SIZE> for RISCVCycle<VirtualShiftR
 
     fn to_lookup_operands(&self) -> (u64, u128) {
         let (x, y) = LookupQuery::<WORD_SIZE>::to_instruction_inputs(self);
-        (0, x as u128 + y as u128)
+        (0, x as u128 + y as u64 as u128)
     }
 
     fn to_lookup_index(&self) -> u128 {
```

### jolt-core/src/zkvm/instruction/virtual_shift_right_bitmaski.rs
```diff
@@ -37,7 +37,7 @@ impl<const WORD_SIZE: usize> LookupQuery<WORD_SIZE> for RISCVCycle<VirtualShiftR
 
     fn to_lookup_operands(&self) -> (u64, u128) {
         let (x, y) = LookupQuery::<WORD_SIZE>::to_instruction_inputs(self);
-        (0, x as u128 + y as u128)
+        (0, x as u128 + y as u64 as u128)
     }
 
     fn to_lookup_index(&self) -> u128 {
```
