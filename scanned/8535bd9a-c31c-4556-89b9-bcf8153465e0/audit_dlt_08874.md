# [?] Include missing patch name in panic. (#3913)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2023-08-20
Source: https://github.com/starkware-libs/cairo/commit/7fb7e055bc6c06c5a2817a0fc1006e6cee25d4e1
Type: security-commit

## Details
Include missing patch name in panic. (#3913)

## Patch
### crates/cairo-lang-defs/src/patcher.rs
```diff
@@ -184,7 +184,9 @@ impl RewriteNode {
             }
             // Replace the substring with the relevant rewrite node.
             // TODO(yuval): this currently panics. Fix it.
-            children.push(patches[&name].clone());
+            children.push(
+                patches.get(&name).cloned().unwrap_or_else(|| panic!("No patch named {}.", name)),
+            );
         }
         // Flush the remaining text as a text child.
         if !pending_text.is_empty() {
```
