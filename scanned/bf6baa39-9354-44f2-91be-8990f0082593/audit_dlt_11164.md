# [?] fix: slice reader overflow bounds (#987)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2026-05-01
Source: https://github.com/0xMiden/miden-vm/commit/75f69996d9adb4a9a1c003130f2bef07cb1b5680
Type: security-commit

## Details
fix: slice reader overflow bounds (#987)

## Patch
### CHANGELOG.md
```diff
@@ -6,6 +6,7 @@
 - [BREAKING] Changed `SmtLeaf::hash` to perform domain-separated hashing, reducing the risk of a collision with the hash of an inner node. Miden VM **must** be updated to comply with this.
 - Fixed `SimpleSmt::set_subtree()` to clear stale leaves and inner nodes in the replaced subtree region ([#981](https://github.com/0xMiden/crypto/pull/981)).
 - [BREAKING] Extracted `SmtStorageReader` and `SparseMerkleTreeReader`, allowing `LargeSmt<S>` to work with read-only storage backends ([#967](https://github.com/0xMiden/crypto/pull/967)).
+- Fixed `SliceReader` bounds checking to reject overflowing read lengths ([#987](https://github.com/0xMiden/crypto/pull/987)).
 
 ## 0.24.0 (2026-04-19)
 
```

### miden-serde-utils/src/byte_reader.rs
```diff
@@ -754,10 +754,11 @@ impl ByteReader for SliceReader<'_> {
     }
 
     fn check_eor(&self, num_bytes: usize) -> Result<(), DeserializationError> {
-        if self.pos + num_bytes > self.source.len() {
-            return Err(DeserializationError::UnexpectedEOF);
-        }
-        Ok(())
+        self.pos
+            .checked_add(num_bytes)
+            .filter(|end| *end <= self.source.len())
+            .map(|_| ())
+            .ok_or(DeserializationError::UnexpectedEOF)
     }
 
     fn has_more_bytes(&self) -> bool {
@@ -1173,6 +1174,16 @@ mod tests {
         assert_eq!(reader.max_alloc(8), usize::MAX);
     }
 
+    #[test]
+    fn slice_reader_rejects_overflowing_read_lengths() {
+        let data = [1u8];
+        let mut reader = SliceReader::new(&data);
+
+        assert_eq!(reader.read_u8().unwrap(), 1);
+        assert_eq!(reader.read_slice(usize::MAX), Err(DeserializationError::UnexpectedEOF));
+        assert_eq!(reader.check_eor(usize::MAX), Err(DeserializationError::UnexpectedEOF));
+    }
+
     // ============================================================================================
     // The following tests document the threat model and defense layers.
     // ============================================================================================
```
