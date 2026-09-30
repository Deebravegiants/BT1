# [?] fix: support underflow case for sub chip (#63)

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2024-01-10
Source: https://github.com/succinctlabs/sp1/commit/6937babfdf91ea2d04e7536e14b519f6de9e99ac
Type: security-commit

## Details
fix: support underflow case for sub chip (#63)

## Patch
### core/src/alu/add/mod.rs
```diff
@@ -161,7 +161,7 @@ mod tests {
     use p3_poseidon2::{DiffusionMatrixBabybear, Poseidon2};
     use p3_symmetric::{CompressionFunctionFromHasher, SerializingHasher32};
     use p3_uni_stark::{prove, verify, StarkConfigImpl};
-    use rand::thread_rng;
+    use rand::{thread_rng, Rng};
 
     use crate::{
         alu::AluEvent,
@@ -224,6 +224,16 @@ mod tests {
         let mut challenger = Challenger::new(perm.clone());
 
         let mut segment = Segment::default();
+        for _i in 0..1000 {
+            let operand_1 = thread_rng().gen_range(0..u32::MAX);
+            let operand_2 = thread_rng().gen_range(0..u32::MAX);
+            let result = operand_1.wrapping_add(operand_2);
+
+            segment
+                .sub_events
+                .push(AluEvent::new(0, Opcode::SUB, result, operand_1, operand_2));
+        }
+
         segment.add_events = vec![AluEvent::new(0, Opcode::ADD, 14, 8, 6)].repeat(1000);
         let chip = AddChip::new();
         let trace: RowMajorMatrix<BabyBear> = chip.generate_trace(&mut segment);
```

### core/src/alu/sub/mod.rs
```diff
@@ -59,15 +59,17 @@ impl<F: PrimeField> Chip<F> for SubChip {
                 let c = event.c.to_le_bytes();
 
                 let mut carry = [0u8, 0u8, 0u8];
-                if (b[0] as i32) - (c[0] as i32) < 0 {
+                if b[0] < c[0] {
                     carry[0] = 1;
                     cols.carry[0] = F::one();
                 }
-                if (b[1] as u32) - (c[1] as u32) + (carry[0] as u32) > 255 {
+
+                if (b[1] as u16) < c[1] as u16 + carry[0] as u16 {
                     carry[1] = 1;
                     cols.carry[1] = F::one();
                 }
-                if (b[2] as u32) - (c[2] as u32) + (carry[1] as u32) > 255 {
+
+                if (b[2] as u16) < c[2] as u16 + carry[1] as u16 {
                     carry[2] = 1;
                     cols.carry[2] = F::one();
                 }
@@ -109,20 +111,22 @@ where
         let base = AB::F::from_canonical_u32(1 << 8);
 
         // For each limb, assert that difference between the carried result and the non-carried
-        // result is either zero or the base.
+        // result is either zero or minus the base.
+        // Note that the overflow variables can be have a value of -256 (mod P), so the field
+        // should be big enough to handle that.
         let overflow_0 = local.b[0] - local.c[0] - local.a[0];
-        let overflow_1 = local.b[1] - local.c[1] + local.a[1] - local.carry[0];
-        let overflow_2 = local.b[2] - local.c[2] + local.a[2] - local.carry[1];
-        let overflow_3 = local.b[3] - local.c[3] + local.a[3] - local.carry[2];
-        builder.assert_zero(overflow_0.clone() * (overflow_0.clone() - base));
-        builder.assert_zero(overflow_1.clone() * (overflow_1.clone() - base));
-        builder.assert_zero(overflow_2.clone() * (overflow_2.clone() - base));
-        builder.assert_zero(overflow_3.clone() * (overflow_3.clone() - base));
+        let overflow_1 = local.b[1] - local.c[1] - local.a[1] - local.carry[0];
+        let overflow_2 = local.b[2] - local.c[2] - local.a[2] - local.carry[1];
+        let overflow_3 = local.b[3] - local.c[3] - local.a[3] - local.carry[2];
+        builder.assert_zero(overflow_0.clone() * (overflow_0.clone() + base));
+        builder.assert_zero(overflow_1.clone() * (overflow_1.clone() + base));
+        builder.assert_zero(overflow_2.clone() * (overflow_2.clone() + base));
+        builder.assert_zero(overflow_3.clone() * (overflow_3.clone() + base));
 
         // If the carry is one, then the overflow must be the base.
-        builder.assert_zero(local.carry[0] * (overflow_0.clone() - base.clone()));
-        builder.assert_zero(local.carry[1] * (overflow_1.clone() - base.clone()));
-        builder.assert_zero(local.carry[2] * (overflow_2.clone() - base.clone()));
+        builder.assert_zero(local.carry[0] * (overflow_0.clone() + base));
+        builder.assert_zero(local.carry[1] * (overflow_1.clone() + base));
+        builder.assert_zero(local.carry[2] * (overflow_2.clone() + base));
 
         // If the carry is not one, then the overflow must be zero.
         builder.assert_zero((local.carry[0] - one) * overflow_0.clone());
@@ -167,7 +171,7 @@ mod tests {
     use p3_poseidon2::{DiffusionMatrixBabybear, Poseidon2};
     use p3_symmetric::{CompressionFunctionFromHasher, SerializingHasher32};
     use p3_uni_stark::{prove, verify, StarkConfigImpl};
-    use rand::thread_rng;
+    use rand::{thread_rng, Rng};
 
     use crate::{
         alu::AluEvent,
@@ -230,7 +234,16 @@ mod tests {
         let mut challenger = Challenger::new(perm.clone());
 
         let mut segment = Segment::default();
-        segment.sub_events = vec![AluEvent::new(0, Opcode::SUB, 14, 8, 6)].repeat(1000);
+
+        for _i in 0..1000 {
+            let operand_1 = thread_rng().gen_range(0..u32::MAX);
+            let operand_2 = thread_rng().gen_range(0..u32::MAX);
+            let result = operand_1.wrapping_sub(operand_2);
+
+            segment
+                .sub_events
+                .push(AluEvent::new(0, Opcode::SUB, result, operand_1, operand_2));
+        }
         let chip = SubChip::new();
         let trace: RowMajorMatrix<BabyBear> = chip.generate_trace(&mut segment);
         let proof = prove::<MyConfig, _>(&config, &chip, &mut challenger, trace);
```
