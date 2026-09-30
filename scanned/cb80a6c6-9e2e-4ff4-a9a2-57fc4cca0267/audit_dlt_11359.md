# [?] fix: remove panic for adding an invalid crate name in wasm compiler (#3977)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-01-08
Source: https://github.com/noir-lang/noir/commit/7a1baa56faa2deb385ef1b6c9da9073dafd5a376
Type: security-commit

## Details
fix: remove panic for adding an invalid crate name in wasm compiler (#3977)

# Description

## Problem\*

Resolves <!-- Link to GitHub Issue -->

## Summary\*

This PR bubbles up the error message for an invalid crate name rather
than panicking.

## Additional Context



## Documentation\*

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[Exceptional Case]** Documentation to be submitted in a separate
PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### compiler/wasm/src/compile_new.rs
```diff
@@ -79,11 +79,12 @@ impl CompilerContext {
         crate_name: String,
         from: &CrateIDWrapper,
         to: &CrateIDWrapper,
-    ) {
-        let parsed_crate_name: CrateName = crate_name
-            .parse()
-            .unwrap_or_else(|_| panic!("Failed to parse crate name {}", crate_name));
+    ) -> Result<(), JsCompileError> {
+        let parsed_crate_name: CrateName =
+            crate_name.parse().map_err(|err_string| JsCompileError::new(err_string, Vec::new()))?;
+
         add_dep(&mut self.context, from.0, to.0, parsed_crate_name);
+        Ok(())
     }
 
     pub fn compile_program(
@@ -188,7 +189,7 @@ pub fn compile_(
         crate_names.insert(lib_name.clone(), crate_id);
 
         // Add the dependency edges
-        compiler_context.add_dependency_edge(lib_name_string, &root_id, &crate_id);
+        compiler_context.add_dependency_edge(lib_name_string, &root_id, &crate_id)?;
     }
 
     // Process the transitive dependencies of the root
@@ -207,7 +208,11 @@ pub fn compile_(
                 .entry(dependency_name.clone())
                 .or_insert_with(|| add_noir_lib(&mut compiler_context, dependency_name));
 
-            compiler_context.add_dependency_edge(dependency_name_string, &crate_id, dep_crate_id);
+            compiler_context.add_dependency_edge(
+                dependency_name_string,
+                &crate_id,
+                dep_crate_id,
+            )?;
         }
     }
 
@@ -278,8 +283,8 @@ mod test {
         let lib1_crate_id = context.process_dependency_crate("lib1/lib.nr".to_string());
         let root_crate_id = context.root_crate_id();
 
-        context.add_dependency_edge("lib1".to_string(), &root_crate_id, &lib1_crate_id);
-        context.add_dependency_edge("lib1".to_string(), &root_crate_id, &lib1_crate_id);
+        context.add_dependency_edge("lib1".to_string(), &root_crate_id, &lib1_crate_id).unwrap();
+        context.add_dependency_edge("lib1".to_string(), &root_crate_id, &lib1_crate_id).unwrap();
 
         assert_eq!(context.crate_graph().number_of_crates(), 3);
     }
@@ -303,9 +308,9 @@ mod test {
         let lib3_crate_id = context.process_dependency_crate("lib3/lib.nr".to_string());
         let root_crate_id = context.root_crate_id();
 
-        context.add_dependency_edge("lib1".to_string(), &root_crate_id, &lib1_crate_id);
-        context.add_dependency_edge("lib2".to_string(), &lib1_crate_id, &lib2_crate_id);
-        context.add_dependency_edge("lib3".to_string(), &lib2_crate_id, &lib3_crate_id);
+        context.add_dependency_edge("lib1".to_string(), &root_crate_id, &lib1_crate_id).unwrap();
+        context.add_dependency_edge("lib2".to_string(), &lib1_crate_id, &lib2_crate_id).unwrap();
+        context.add_dependency_edge("lib3".to_string(), &lib2_crate_id, &lib3_crate_id).unwrap();
 
         assert_eq!(context.crate_graph().number_of_crates(), 5);
     }
@@ -328,8 +333,8 @@ mod test {
         let lib3_crate_id = context.process_dependency_crate("lib3/lib.nr".to_string());
         let root_crate_id = context.root_crate_id();
 
-        context.add_dependency_edge("lib1".to_string(), &root_crate_id, &lib1_crate_id);
-        context.add_dependency_edge("lib3".to_string(), &lib2_crate_id, &lib3_crate_id);
+        context.add_dependency_edge("lib1".to_string(), &root_crate_id, &lib1_crate_id).unwrap();
+        context.add_dependency_edge("lib3".to_string(), &lib2_crate_id, &lib3_crate_id).unwrap();
 
         assert_eq!(context.crate_graph().number_of_crates(), 5);
     }
```
