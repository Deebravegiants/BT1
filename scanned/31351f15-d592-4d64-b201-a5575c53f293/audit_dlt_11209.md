# [?] fix: out of bounds error when using read/write volatile (#1153)

## Summary
Severity: Unknown
Chain: ZK
Component: a16z/jolt
Published: 2025-12-08
Source: https://github.com/a16z/jolt/commit/933352ee8c63125eedfb2d76eb1d0f19bfa0d7bb
Type: security-commit

## Details
fix: out of bounds error when using read/write volatile (#1153)

Signed-off-by: Andrew Tretyakov <42178850+0xAndoroid@users.noreply.github.com>

## Patch
### jolt-core/src/zkvm/ram/mod.rs
```diff
@@ -328,7 +328,8 @@ pub fn gen_ram_memory_states<F: JoltField>(
     // Note that `final_memory` only contains memory at addresses >= `RAM_START_ADDRESS`
     // so we will still need to populate `final_memory_state` with the contents of
     // `program_io`, which lives at addresses < `RAM_START_ADDRESS`
-    final_memory_state[dram_start_index..]
+    let final_memory_words = final_memory.data.len().min(K - dram_start_index);
+    final_memory_state[dram_start_index..dram_start_index + final_memory_words]
         .par_iter_mut()
         .enumerate()
         .for_each(|(k, word)| {
```
