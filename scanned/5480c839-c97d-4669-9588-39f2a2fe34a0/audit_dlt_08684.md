# [?] avoid overflow panic in debug log call

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2024-01-15
Source: https://github.com/namada-net/namada/commit/8affedad46a2e55644a95bf2b0d4c60dd939f754
Type: security-commit

## Details
avoid overflow panic in debug log call

## Patch
### crates/namada/src/vm/wasm/memory.rs
```diff
@@ -171,10 +171,10 @@ pub fn write_vp_inputs(
 /// it will try to grow the memory.
 fn check_bounds(memory: &Memory, base_offset: u64, len: usize) -> Result<()> {
     tracing::debug!(
-        "check_bounds pages {}, data_size {}, base_offset + len {}",
+        "check_bounds pages {}, data_size {}, base_offset {base_offset}, len \
+         {len}",
         memory.size().0,
         memory.data_size(),
-        base_offset + len as u64
     );
     let desired_offset = base_offset
         .checked_add(len as u64)
```
