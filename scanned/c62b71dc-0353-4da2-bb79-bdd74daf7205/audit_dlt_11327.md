# [?] fix: do not panic on indices which are not valid `u32`s (#6976)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-01-08
Source: https://github.com/noir-lang/noir/commit/bf474c0ee837fdf8809b2785759f86a433122174
Type: security-commit

## Details
fix: do not panic on indices which are not valid `u32`s (#6976)

## Patch
### acvm-repo/acvm/src/pwg/memory_op.rs
```diff
@@ -21,6 +21,19 @@ pub(crate) struct MemoryOpSolver<F> {
 }
 
 impl<F: AcirField> MemoryOpSolver<F> {
+    fn index_from_field(&self, index: F) -> Result<MemoryIndex, OpcodeResolutionError<F>> {
+        if index.num_bits() <= 32 {
+            let memory_index = index.try_to_u64().unwrap() as MemoryIndex;
+            Ok(memory_index)
+        } else {
+            Err(OpcodeResolutionError::IndexOutOfBounds {
+                opcode_location: ErrorLocation::Unresolved,
+                index,
+                array_size: self.block_len,
+            })
+        }
+    }
+
     fn write_memory_index(
         &mut self,
         index: MemoryIndex,
@@ -29,7 +42,7 @@ impl<F: AcirField> MemoryOpSolver<F> {
         if index >= self.block_len {
             return Err(OpcodeResolutionError::IndexOutOfBounds {
                 opcode_location: ErrorLocation::Unresolved,
-                index,
+                index: F::from(index as u128),
                 array_size: self.block_len,
             });
         }
@@ -40,7 +53,7 @@ impl<F: AcirField> MemoryOpSolver<F> {
     fn read_memory_index(&self, index: MemoryIndex) -> Result<F, OpcodeResolutionError<F>> {
         self.block_value.get(&index).copied().ok_or(OpcodeResolutionError::IndexOutOfBounds {
             opcode_location: ErrorLocation::Unresolved,
-            index,
+            index: F::from(index as u128),
             array_size: self.block_len,
         })
     }
@@ -72,7 +85,7 @@ impl<F: AcirField> MemoryOpSolver<F> {
 
         // Find the memory index associated with this memory operation.
         let index = get_value(&op.index, initial_witness)?;
-        let memory_index = index.try_to_u64().unwrap() as MemoryIndex;
+        let memory_index = self.index_from_field(index)?;
 
         // Calculate the value associated with this memory operation.
         //
@@ -193,9 +206,9 @@ mod tests {
             err,
             Some(crate::pwg::OpcodeResolutionError::IndexOutOfBounds {
                 opcode_location: _,
-                index: 2,
+                index,
                 array_size: 2
-            })
+            }) if index == FieldElement::from(2u128)
         ));
     }
 
```

### acvm-repo/acvm/src/pwg/mod.rs
```diff
@@ -126,7 +126,7 @@ pub enum OpcodeResolutionError<F> {
         payload: Option<ResolvedAssertionPayload<F>>,
     },
     #[error("Index out of bounds, array has size {array_size:?}, but index was {index:?}")]
-    IndexOutOfBounds { opcode_location: ErrorLocation, index: u32, array_size: u32 },
+    IndexOutOfBounds { opcode_location: ErrorLocation, index: F, array_size: u32 },
     #[error("Cannot solve opcode: {invalid_input_bit_size}")]
     InvalidInputBitSize {
         opcode_location: ErrorLocation,
```
