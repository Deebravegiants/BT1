# [?] fix(chisel): don't panic on bad pc/memory (#12674)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-11-27
Source: https://github.com/foundry-rs/foundry/commit/48001a5df53bf9111914792de64f8b71a1005730
Type: security-commit

## Details
fix(chisel): don't panic on bad pc/memory (#12674)

## Patch
### crates/chisel/src/executor.rs
```diff
@@ -152,11 +152,17 @@ impl SessionSource {
 
         // the file compiled correctly, thus the last stack item must be the memory offset of
         // the `bytes memory inspectoor` value
-        let mut offset = stack.last().unwrap().to::<usize>();
-        let mem_offset = &memory[offset..offset + 32];
-        let len = U256::try_from_be_slice(mem_offset).unwrap().to::<usize>();
-        offset += 32;
-        let data = &memory[offset..offset + len];
+        let data = (|| -> Option<_> {
+            let mut offset: usize = stack.last()?.try_into().ok()?;
+            debug!("inspect memory @ {offset}: {}", hex::encode(memory));
+            let mem_offset = memory.get(offset..offset + 32)?;
+            let len: usize = U256::try_from_be_slice(mem_offset)?.try_into().ok()?;
+            offset += 32;
+            memory.get(offset..offset + len)
+        })();
+        let Some(data) = data else {
+            eyre::bail!("Failed to inspect last expression: could not retrieve data from memory")
+        };
         let token = ty.abi_decode(data).wrap_err("Could not decode inspected values")?;
         let c = if should_continue(contract_expr) {
             ControlFlow::Continue(())
```
