# [?] Fix overflow check and test. Remove [..8] when using h256_limbs.

## Summary
Severity: Unknown
Chain: ZK
Component: 0xPolygonZero/plonky2
Published: 2023-09-05
Source: https://github.com/0xPolygonZero/plonky2/commit/1c01d682aad36c37a4f294297ed8fc6499f920c0
Type: security-commit

## Details
Fix overflow check and test. Remove [..8] when using h256_limbs.

## Patch
### evm/src/cpu/kernel/asm/memory/metadata.asm
```diff
@@ -247,9 +247,12 @@ global blockhash:
     // stack: block_number, retdest
     %mload_global_metadata(@GLOBAL_METADATA_BLOCK_NUMBER)
     // stack: cur_block_number, block_number, retdest
+    // Check for an overflow, since we're incrementing `block_number` afterwards.
+    DUP2 %eq_const(@U256_MAX) %jumpi(zero_hash)
+    // stack: cur_block_number, block_number, retdest
     DUP1 DUP3 %increment GT %jumpi(zero_hash) // if block_number >= cur_block_number
     // stack: cur_block_number, block_number, retdest
-    DUP2 PUSH 256 %add_or_fault
+    DUP2 PUSH 256 ADD
     // stack: block_number+256, cur_block_number, block_number, retdest
     DUP2 GT %jumpi(zero_hash) // if cur_block_number > block_number + 256
     // If we are here, the provided block number is correct
```

### evm/src/cpu/kernel/tests/block_hash.rs
```diff
@@ -97,8 +97,7 @@ fn test_small_index_block_hash() -> Result<()> {
 }
 
 #[test]
-#[should_panic]
-fn test_block_hash_with_overflow() {
+fn test_block_hash_with_overflow() -> Result<()> {
     let blockhash_label = KERNEL.global_labels["blockhash"];
     let retdest = 0xDEADBEEFu32.into();
     let cur_block_number = 1;
@@ -111,5 +110,16 @@ fn test_block_hash_with_overflow() {
     interpreter.set_memory_segment(Segment::BlockHashes, hashes[0..256].to_vec());
     interpreter.set_global_metadata_field(GlobalMetadata::BlockCurrentHash, hashes[256]);
     interpreter.set_global_metadata_field(GlobalMetadata::BlockNumber, cur_block_number.into());
-    let _ = interpreter.run();
+    interpreter.run()?;
+
+    let result = interpreter.stack();
+    assert_eq!(
+        result[0],
+        0.into(),
+        "Resulting block hash {:?} different from expected hash {:?}",
+        result[0],
+        0
+    );
+
+    Ok(())
 }
```

### evm/src/get_challenges.rs
```diff
@@ -155,9 +155,9 @@ fn observe_block_hashes<
     block_hashes: &BlockHashes,
 ) {
     for i in 0..256 {
-        challenger.observe_elements(&h256_limbs::<F>(block_hashes.prev_hashes[i])[0..8]);
+        challenger.observe_elements(&h256_limbs::<F>(block_hashes.prev_hashes[i]));
     }
-    challenger.observe_elements(&h256_limbs::<F>(block_hashes.cur_hash)[0..8]);
+    challenger.observe_elements(&h256_limbs::<F>(block_hashes.cur_hash));
 }
 
 fn observe_block_hashes_target<
```

### evm/src/recursive_verifier.rs
```diff
@@ -1057,17 +1057,15 @@ pub(crate) fn set_block_hashes_target<F, W, const D: usize>(
     W: Witness<F>,
 {
     for i in 0..256 {
-        let block_hash_limbs: [F; 8] = h256_limbs::<F>(block_hashes.prev_hashes[i])[..8]
+        let block_hash_limbs: [F; 8] = h256_limbs::<F>(block_hashes.prev_hashes[i])
             .try_into()
             .unwrap();
         witness.set_target_arr(
             &block_hashes_target.prev_hashes[8 * i..8 * (i + 1)],
             &block_hash_limbs,
         );
     }
-    let cur_block_hash_limbs: [F; 8] = h256_limbs::<F>(block_hashes.cur_hash)[..8]
-        .try_into()
-        .unwrap();
+    let cur_block_hash_limbs: [F; 8] = h256_limbs::<F>(block_hashes.cur_hash).try_into().unwrap();
     witness.set_target_arr(&block_hashes_target.cur_hash, &cur_block_hash_limbs);
 }
 
```
