# [?] fix: race condition in rpctypegen macro (#7763)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2022-10-04
Source: https://github.com/near/nearcore/commit/5ab9a83cae8a5cfc18def2e09eeb74e7ac355c48
Type: security-commit

## Details
fix: race condition in rpctypegen macro (#7763)

The macro can be invoked by several processes, so we need some kind of
IPC lock here to avoid reading garbage data.

File locks are a sketchy technology, but what we are doing here is
already quite gross :-)

closes https://github.com/near/nearcore/issues/7757

## Patch
### Cargo.lock
```diff
@@ -3398,6 +3398,7 @@ dependencies = [
 name = "near-rpc-error-macro"
 version = "0.0.0"
 dependencies = [
+ "fs2",
  "near-rpc-error-core",
  "serde",
  "serde_json",
```

### tools/rpctypegen/macro/Cargo.toml
```diff
@@ -19,6 +19,7 @@ proc-macro = true
 serde.workspace = true
 serde_json = { workspace = true, optional = true, features = ["preserve_order"] }
 syn.workspace = true
+fs2.workspace = true
 
 near-rpc-error-core = { path = "../core" }
 
```

### tools/rpctypegen/macro/src/lib.rs
```diff
@@ -32,23 +32,84 @@ fn merge(a: &mut Value, b: &Value) {
 
 #[cfg(feature = "dump_errors_schema")]
 impl Drop for Schema {
+    /// `rpc_error` wants to collect **all** invocations of the macro across the
+    /// project and merge them into a single file. These kinds of macros are not
+    /// supported at all by Rust macro infrastructure, so we use gross hacks
+    /// here.
+    ///
+    /// Every macro invocation merges its results into the
+    /// rpc_errors_schema.json file, with the file playing the role of global
+    /// mutable state which can be accessed from different processes. To avoid
+    /// race conditions, we use file-locking. File locking isn't a very robust
+    /// thing, but it should ok be considering the level of hack here.
     fn drop(&mut self) {
+        use fs2::FileExt;
+        use std::fs::File;
+        use std::io::{Read, Seek, SeekFrom, Write};
+
+        struct Guard {
+            file: File,
+        }
+        impl Guard {
+            fn new(path: &str) -> Self {
+                let file = File::options()
+                    .read(true)
+                    .write(true)
+                    .create_new(true)
+                    .open(path)
+                    .or_else(|_| File::options().read(true).write(true).open(path))
+                    .unwrap_or_else(|err| panic!("can't open {path}: {err}"));
+                file.lock_exclusive().unwrap_or_else(|err| panic!("can't lock {path}: {err}"));
+                Guard { file }
+            }
+        }
+        impl Drop for Guard {
+            fn drop(&mut self) {
+                let _ = self.file.unlock();
+            }
+        }
+
+        let schema_json = serde_json::to_value(self).expect("Schema serialize failed");
+
         // std::env::var("CARGO_TARGET_DIR") doesn't exists
         let filename = "./target/rpc_errors_schema.json";
-        let schema_json = serde_json::to_value(self).expect("Schema serialize failed");
-        let new_schema_json = if let Ok(data) = std::fs::read(filename) {
-            // merge to the existing file
-            let mut existing_schema = serde_json::from_slice::<Value>(&data)
-                .expect("cannot deserialize target/existing_schema.json");
-            merge(&mut existing_schema, &schema_json);
-            existing_schema
-        } else {
-            schema_json
+        let mut guard = Guard::new(filename);
+
+        let existing_schema: Option<Value> = {
+            let mut buf = Vec::new();
+            guard
+                .file
+                .read_to_end(&mut buf)
+                .unwrap_or_else(|err| panic!("can't read {filename}: {err}"));
+            if buf.is_empty() {
+                None
+            } else {
+                let json = serde_json::from_slice(&buf)
+                    .unwrap_or_else(|err| panic!("can't deserialize {filename}: {err}"));
+                Some(json)
+            }
+        };
+
+        let new_schema_json = match existing_schema {
+            None => schema_json,
+            Some(mut existing_schema) => {
+                merge(&mut existing_schema, &schema_json);
+                existing_schema
+            }
         };
+
         let new_schema_json_string = serde_json::to_string_pretty(&new_schema_json)
             .expect("error schema serialization failed");
-        std::fs::write(filename, new_schema_json_string)
-            .expect("Unable to save the errors schema file");
+
+        guard.file.set_len(0).unwrap_or_else(|err| panic!("can't truncate {filename}: {err}"));
+        guard
+            .file
+            .seek(SeekFrom::Start(0))
+            .unwrap_or_else(|err| panic!("can't seek {filename}: {err}"));
+        guard
+            .file
+            .write_all(new_schema_json_string.as_bytes())
+            .unwrap_or_else(|err| panic!("can't write {filename}: {err}"));
     }
 }
 
```
