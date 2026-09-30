# [?] fix(debugger): don't panic on pc-ic / sourcemap mismatch (#7991)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-05-24
Source: https://github.com/foundry-rs/foundry/commit/10f1402b9dc7c4d0fdffd47d5c842cf416f656ea
Type: security-commit

## Details
fix(debugger): don't panic on pc-ic / sourcemap mismatch (#7991)

## Patch
### crates/debugger/src/tui/draw.rs
```diff
@@ -350,17 +350,18 @@ impl DebuggerContext<'_> {
                 } else {
                     contract_source.deployed_bytecode.bytecode.as_ref()?
                 };
-                let mut source_map = bytecode.source_map()?.ok()?;
+                let source_map = bytecode.source_map()?.ok()?;
 
                 let pc_ic_map = if is_create { create_map } else { rt_map };
                 let ic = pc_ic_map.get(pc)?;
-                let source_element = source_map.swap_remove(ic);
+                let source_element = source_map.get(ic)?;
                 // if the source element has an index, find the sourcemap for that index
                 source_element
                     .index
-                    .and_then(|index|
                     // if index matches current file_id, return current source code
-                    (index == file_id).then(|| (source_element.clone(), source_code)))
+                    .and_then(|index| {
+                        (index == file_id).then(|| (source_element.clone(), source_code))
+                    })
                     .or_else(|| {
                         // otherwise find the source code for the element's index
                         self.debugger
```
