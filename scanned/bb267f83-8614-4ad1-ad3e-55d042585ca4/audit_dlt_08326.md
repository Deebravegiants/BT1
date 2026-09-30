# [?] [vm] Fix out-of-bounds reads in MonoMove tests (#20609)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-09-24
Source: https://github.com/aptos-labs/aptos-core/commit/ab5b6cbcfa679f530a0ac081a03552944737bc69
Type: security-commit

## Details
[vm] Fix out-of-bounds reads in MonoMove tests (#20609)

## Patch
### third_party/move/mono-move/runtime/src/interpreter.rs
```diff
@@ -716,14 +716,11 @@ impl<'guard> InterpreterContext<'guard> {
 
     /// Read a u64 from the root frame's slot 0 (where the result lands).
     pub fn root_result_u64_for_test(&self) -> u64 {
+        // SAFETY: the caller guarantees a completed call that wrote an 8-byte
+        // result to slot 0, so every byte read is initialized.
         unsafe { read_u64(self.stack.as_ptr(), FRAME_METADATA_SIZE) }
     }
 
-    /// Read a u64 from the root frame at the given byte offset.
-    pub fn root_result_u64_at_for_test(&self, offset: u32) -> u64 {
-        unsafe { read_u64(self.stack.as_ptr(), FRAME_METADATA_SIZE + offset as usize) }
-    }
-
     /// BCS-serializes the value a successfully completed root call returned.
     /// Call only after a successful run, with `ty` that call's return type;
     /// the result lives at the start of the root frame's shared
@@ -741,6 +738,8 @@ impl<'guard> InterpreterContext<'guard> {
     /// Read `size` raw bytes from the root frame at the given byte offset. For
     /// tests inspecting an entry/native function's raw return slots.
     pub fn root_result_bytes_for_test(&self, offset: u32, size: u32) -> &[u8] {
+        // SAFETY: the caller guarantees a completed call that wrote all `size`
+        // bytes at `offset`, so the slice lies in the stack and is initialized.
         unsafe {
             let base = self
                 .stack
```

### third_party/move/mono-move/runtime/tests/int_ops.rs
```diff
@@ -256,16 +256,9 @@ fn run_wide(
         }
         call.run().map_err(|e| anyhow::anyhow!("{}", e))?;
 
-        let mut out = vec![0u8; dst_size];
-        let mut i = 0usize;
-        while i < dst_size {
-            let word = ctx.root_result_u64_at_for_test(SLOT_DST + i as u32);
-            let bytes = word.to_ne_bytes();
-            let copy_n = (dst_size - i).min(8);
-            out[i..i + copy_n].copy_from_slice(&bytes[..copy_n]);
-            i += 8;
-        }
-        Ok(out)
+        Ok(ctx
+            .root_result_bytes_for_test(SLOT_DST, dst_size as u32)
+            .to_vec())
     })
 }
 
```
