# [?] Fix build script stack overflow

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-05-21
Source: https://github.com/RaoFoundation/subtensor/commit/3bda8a132cca11af513f59251f053b8626d19bc7
Type: security-commit

## Details
Fix build script stack overflow

## Patch
### build.rs
```diff
@@ -29,45 +29,52 @@ fn main() {
     // as we process each Rust file
     let (tx, rx) = channel();
 
-    // Parse each rust file with syn and run the linting suite on it in parallel
-    rust_files.par_iter().for_each_with(tx.clone(), |tx, file| {
-        let is_test = file.display().to_string().contains("test");
-        let Ok(content) = fs::read_to_string(file) else {
-            return;
-        };
-        let Ok(parsed_tokens) = proc_macro2::TokenStream::from_str(&content) else {
-            return;
-        };
-        let Ok(parsed_file) = syn::parse2::<syn::File>(parsed_tokens) else {
-            return;
-        };
+    let pool = rayon::ThreadPoolBuilder::new()
+        .stack_size(64 * 1024 * 1024)
+        .build()
+        .expect("build script lint thread pool can be created");
 
-        let track_lint = |result: Result| {
-            let Err(errors) = result else {
+    pool.install(|| {
+        // Parse each rust file with syn and run the linting suite on it in parallel.
+        rust_files.par_iter().for_each_with(tx.clone(), |tx, file| {
+            let is_test = file.display().to_string().contains("test");
+            let Ok(content) = fs::read_to_string(file) else {
                 return;
             };
-            let relative_path = file.strip_prefix(workspace_root).unwrap_or(file.as_path());
-            for error in errors {
-                let loc = error.span().start();
-                let file_path = relative_path.display();
-                // note that spans can't go across thread boundaries without losing their location
-                // info so we we serialize here and send a String
-                tx.send(format!(
-                    "cargo:warning={}:{}:{}: {}",
-                    file_path, loc.line, loc.column, error,
-                ))
-                .unwrap();
-            }
-        };
+            let Ok(parsed_tokens) = proc_macro2::TokenStream::from_str(&content) else {
+                return;
+            };
+            let Ok(parsed_file) = syn::parse2::<syn::File>(parsed_tokens) else {
+                return;
+            };
+
+            let track_lint = |result: Result| {
+                let Err(errors) = result else {
+                    return;
+                };
+                let relative_path = file.strip_prefix(workspace_root).unwrap_or(file.as_path());
+                for error in errors {
+                    let loc = error.span().start();
+                    let file_path = relative_path.display();
+                    // note that spans can't go across thread boundaries without losing their location
+                    // info so we we serialize here and send a String
+                    tx.send(format!(
+                        "cargo:warning={}:{}:{}: {}",
+                        file_path, loc.line, loc.column, error,
+                    ))
+                    .unwrap();
+                }
+            };
 
-        track_lint(ForbidAsPrimitiveConversion::lint(&parsed_file));
-        track_lint(ForbidKeysRemoveCall::lint(&parsed_file));
-        track_lint(RequireFreezeStruct::lint(&parsed_file));
-        track_lint(RequireExplicitPalletIndex::lint(&parsed_file));
+            track_lint(ForbidAsPrimitiveConversion::lint(&parsed_file));
+            track_lint(ForbidKeysRemoveCall::lint(&parsed_file));
+            track_lint(RequireFreezeStruct::lint(&parsed_file));
+            track_lint(RequireExplicitPalletIndex::lint(&parsed_file));
 
-        if is_test {
-            track_lint(ForbidSaturatingMath::lint(&parsed_file));
-        }
+            if is_test {
+                track_lint(ForbidSaturatingMath::lint(&parsed_file));
+            }
+        });
     });
 
     // Collect and print all errors after the parallel processing is done
```

### support/procedural-fork/Cargo.toml
```diff
@@ -10,7 +10,7 @@ all = "allow"
 derive-syn-parse.workspace = true
 Inflector.workspace = true
 cfg-expr.workspace = true
-itertools.workspace = true
+itertools = { workspace = true, features = ["use_alloc"] }
 proc-macro2.workspace = true
 quote.workspace = true
 syn = { workspace = true, features = [
```
