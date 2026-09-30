# [?] fix(lsp): don't fail on out-of-bounds position (#12462)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-04-28
Source: https://github.com/noir-lang/noir/commit/5610ecb2ac11bc8c1da2693c95db5a4c9ae2e4c0
Type: security-commit

## Details
fix(lsp): don't fail on out-of-bounds position (#12462)

## Patch
### tooling/lsp/src/requests/mod.rs
```diff
@@ -496,21 +496,16 @@ fn position_to_location(
     files: &FileMap,
     file_path: &PathString,
     position: &Position,
-) -> Result<noirc_errors::Location, ResponseError> {
-    let file_id = file_path_to_file_id(files, file_path)?;
-    let byte_index = position_to_byte_index(files, file_id, position).map_err(|err| {
-        ResponseError::new(
-            ErrorCode::REQUEST_FAILED,
-            format!("Could not convert position to byte index. Error: {err:?}"),
-        )
-    })?;
+) -> Option<noirc_errors::Location> {
+    let file_id = file_path_to_file_id(files, file_path).ok()?;
+    let byte_index = position_to_byte_index(files, file_id, position).ok()?;
 
     let location = noirc_errors::Location {
         file: file_id,
         span: noirc_errors::Span::single_char(byte_index as u32),
     };
 
-    Ok(location)
+    Some(location)
 }
 
 pub(crate) fn file_path_to_file_id(
@@ -640,11 +635,13 @@ where
 
     let files = file_manager.as_file_map();
 
-    let location = position_to_location(
+    let Some(location) = position_to_location(
         files,
         &PathString::from(file_path),
         &text_document_position_params.position,
-    )?;
+    ) else {
+        return Ok(T::default());
+    };
 
     Ok(callback(ProcessRequestCallbackArgs {
         location,
@@ -712,11 +709,13 @@ where
 
     let files = workspace_file_manager.as_file_map();
 
-    let location = position_to_location(
+    let Some(location) = position_to_location(
         files,
         &PathString::from(file_path),
         &text_document_position_params.position,
-    )?;
+    ) else {
+        return Ok(T::default());
+    };
 
     Ok(callback(ProcessRequestCallbackArgs {
         location,
```
