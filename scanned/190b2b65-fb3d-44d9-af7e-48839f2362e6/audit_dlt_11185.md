# [?] Merge pull request #479 from 0xKanekiKen/overflow-air-fix

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2022-11-07
Source: https://github.com/0xMiden/miden-vm/commit/b25ab1d62c765fe17435a8a16e77eb58bf91b5a5
Type: security-commit

## Details
Merge pull request #479 from 0xKanekiKen/overflow-air-fix

Fix the overflow stack depth air constraint

## Patch
### air/src/stack/overflow/mod.rs
```diff
@@ -75,7 +75,8 @@ pub fn enforce_stack_depth_constraints<E: FieldElement>(
 ) -> usize {
     let depth = frame.stack_depth();
     let depth_next = frame.stack_depth_next();
-    let no_shift_part = (depth_next - depth) * (E::ONE - op_flag.call() - frame.is_call_end());
+    let no_shift_part =
+        (depth_next - depth) * (E::ONE - op_flag.call() - (op_flag.end() * frame.is_call_end()));
     let left_shift_part = op_flag.left_shift() * op_flag.overflow();
     let right_shift_part = op_flag.right_shift();
     let call_part = op_flag.call() * (depth_next - E::from(16u32));
```

### air/src/stack/overflow/tests.rs
```diff
@@ -96,7 +96,7 @@ fn test_stack_overflow_constraints() {
 }
 
 #[test]
-fn test_stack_depth_air_fail() {
+fn test_stack_depth_air() {
     let depth = 16 + rand_value::<u32>() as u64;
     // block with a control block opcode.
     let mut frame = generate_evaluation_frame(Operation::Split.op_code().into());
@@ -111,17 +111,17 @@ fn test_stack_depth_air_fail() {
     frame.current_mut()[DECODER_TRACE_OFFSET + IS_CALL_FLAG_COL_IDX] =
         Felt::new(rand_value::<u32>() as u64);
     frame.current_mut()[B1_COL_IDX] = Felt::new(12);
-    frame.current_mut()[H0_COL_IDX] = ONE;
+    frame.current_mut()[H0_COL_IDX] = Felt::new(depth - 16).inv();
 
     frame.next_mut()[CLK_COL_IDX] = ONE;
     frame.next_mut()[B0_COL_IDX] = Felt::new(depth - 1);
-    frame.current_mut()[B1_COL_IDX] = Felt::new(12);
-    frame.current_mut()[H0_COL_IDX] = ONE;
+    frame.next_mut()[B1_COL_IDX] = Felt::new(12);
+    frame.next_mut()[H0_COL_IDX] = Felt::new(depth - 1 - 16).inv();
 
     let expected = [Felt::ZERO; NUM_CONSTRAINTS];
     let result = get_constraint_evaluation(frame);
 
-    assert_ne!(expected, result);
+    assert_eq!(expected, result);
 }
 
 // TEST HELPERS
```
