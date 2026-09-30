# [?] fix(cheatcodes): get artifact code panic (#8546)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-07-28
Source: https://github.com/foundry-rs/foundry/commit/682286017eea36ee6309fc659a41167f265c56db
Type: security-commit

## Details
fix(cheatcodes): get artifact code panic (#8546)

## Patch
### crates/cheatcodes/src/fs.rs
```diff
@@ -387,22 +387,21 @@ fn get_artifact_code(state: &Cheatcodes, path: &str, deployed: bool) -> Result<B
                 })
                 .collect::<Vec<_>>();
 
-            let artifact = match filtered.len() {
-                0 => Err(fmt_err!("No matching artifact found")),
-                1 => Ok(filtered[0]),
-                _ => {
+            let artifact = match &filtered[..] {
+                [] => Err(fmt_err!("No matching artifact found")),
+                [artifact] => Ok(artifact),
+                filtered => {
                     // If we know the current script/test contract solc version, try to filter by it
                     state
                         .config
                         .running_version
                         .as_ref()
                         .and_then(|version| {
                             let filtered = filtered
-                                .into_iter()
+                                .iter()
                                 .filter(|(id, _)| id.version == *version)
                                 .collect::<Vec<_>>();
-
-                            (filtered.len() == 1).then_some(filtered[0])
+                            (filtered.len() == 1).then(|| filtered[0])
                         })
                         .ok_or_else(|| fmt_err!("Multiple matching artifacts found"))
                 }
```
