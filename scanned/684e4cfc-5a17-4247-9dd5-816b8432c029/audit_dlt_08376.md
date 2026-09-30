# [?] [fuzzing][storage] fix shift overflow bug

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2020-08-27
Source: https://github.com/move-language/move/commit/121c8651cc19bd31fa641da022608edad47c4cda
Type: security-commit

## Details
[fuzzing][storage] fix shift overflow bug

Closes: #5800

## Patch
### storage/libradb/src/schema/transaction_accumulator/mod.rs
```diff
@@ -35,9 +35,8 @@ impl KeyCodec<TransactionAccumulatorSchema> for Position {
 
     fn decode_key(data: &[u8]) -> Result<Self> {
         ensure_slice_len_eq(data, size_of::<u64>())?;
-        Ok(Position::from_postorder_index(
-            (&data[..]).read_u64::<BigEndian>()?,
-        ))
+        let index = (&data[..]).read_u64::<BigEndian>()?;
+        Ok(Position::from_postorder_index(index)?)
     }
 }
 
```

### types/src/proof/position/mod.rs
```diff
@@ -24,6 +24,7 @@
 //! Note3: The leaf index starting from left-most leaf, starts from 0
 
 use crate::proof::definition::{LeafCount, MAX_ACCUMULATOR_LEAVES, MAX_ACCUMULATOR_PROOF_DEPTH};
+use anyhow::{ensure, Result};
 use mirai_annotations::*;
 use std::fmt;
 
@@ -75,8 +76,13 @@ impl Position {
         self.0
     }
 
-    pub fn from_postorder_index(index: u64) -> Self {
-        Position(postorder_to_inorder(index))
+    pub fn from_postorder_index(index: u64) -> Result<Self> {
+        ensure!(
+            index < (!0u64 >> 2),
+            "node index {} is invalid (greater than 2^63 - 1)",
+            index
+        );
+        Ok(Position(postorder_to_inorder(index)))
     }
 
     pub fn to_postorder_index(self) -> u64 {
```
