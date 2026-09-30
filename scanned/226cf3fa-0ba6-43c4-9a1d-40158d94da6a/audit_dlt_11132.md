# [?] fix OOB slab panic when creating runnables on a did_save event (#6575)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2024-09-21
Source: https://github.com/FuelLabs/sway/commit/3a6e937f9977e9e2e9bb3eebd602b0d5e7cf94a3
Type: security-commit

## Details
fix OOB slab panic when creating runnables on a did_save event (#6575)

## Description
I noticed that the language server would crash when compilation was
triggered from a did save event as we were trying to create runnables
from the Engines that had GC applied to it. We now check to ensure that
the correct Engines is accessed to avoid a panic when creating
runnables.

After fixing this bug, I noticed that optimised builds was not returning
diagnostics. I've opened #6576 to work on this and have temporarily
disabled the optimisation so diagnostics continue to work.

## Checklist

- [x] I have linked to any relevant issues.
- [x] I have commented my code, particularly in hard-to-understand
areas.
- [x] I have updated the documentation where relevant (API docs, the
reference, and the Sway book).
- [ ] If my change requires substantial documentation changes, I have
[requested support from the DevRel
team](https://github.com/FuelLabs/devrel-requests/issues/new/choose)
- [x] I have added tests that prove my fix is effective or that my
feature works.
- [x] I have added (or requested a maintainer to add) the necessary
`Breaking*` or `New Feature` labels where relevant.
- [x] I have done my best to ensure that my PR adheres to [the Fuel Labs
Code Review
Standards](https://github.com/FuelLabs/rfcs/blob/master/text/code-standards/external-contributors.md).
- [x] I have requested a review from the relevant team or maintainers.

## Patch
### sway-lsp/src/core/session.rs
```diff
@@ -477,7 +477,18 @@ pub fn parse_project(
 
     if let Some(typed) = &session.compiled_program.read().typed {
         session.runnables.clear();
-        create_runnables(&session.runnables, typed, engines.de(), engines.se());
+        let path = uri.to_file_path().unwrap();
+        let program_id = program_id_from_path(&path, engines)?;
+        if let Some(metrics) = session.metrics.get(&program_id) {
+            // Check if the cached AST was returned by the compiler for the users workspace.
+            // If it was, then we need to use the original engines.
+            let engines = if metrics.reused_programs > 0 {
+                &*session.engines.read()
+            } else {
+                engines
+            };
+            create_runnables(&session.runnables, typed, engines.de(), engines.se());
+        }
     }
     Ok(())
 }
```

### sway-lsp/src/handlers/notification.rs
```diff
@@ -111,7 +111,8 @@ pub async fn handle_did_change_text_document(
         session.clone(),
         &uri,
         Some(params.text_document.version),
-        true,
+        // TODO: Set this back to true once https://github.com/FuelLabs/sway/issues/6576 is fixed.
+        false,
         file_versions,
     );
     Ok(())
```
