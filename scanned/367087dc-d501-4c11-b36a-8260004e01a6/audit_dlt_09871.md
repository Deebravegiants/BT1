# [?] cherry pick (rest-api): avoid panicking when constructing response headers (#4178)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2024-12-03
Source: https://github.com/iotaledger/iota/commit/1c2f8a60e37f8ace2236efc81a508710aed93844
Type: security-commit

## Details
cherry pick (rest-api): avoid panicking when constructing response headers (#4178)

Co-authored-by: Bing-Yang <51323441+bingyanglin@users.noreply.github.com>

## Patch
### crates/iota-rest-api/src/response.rs
```diff
@@ -130,61 +130,43 @@ pub async fn append_info_headers(
     State(state): State<RestService>,
     response: Response,
 ) -> impl IntoResponse {
-    let latest_checkpoint = state.reader.inner().get_latest_checkpoint().unwrap();
-    let lowest_available_checkpoint = state
-        .reader
-        .inner()
-        .get_lowest_available_checkpoint()
-        .unwrap();
+    let mut headers = HeaderMap::new();
+
+    if let Ok(chain_id) = state.chain_id().to_string().try_into() {
+        headers.insert(X_IOTA_CHAIN_ID, chain_id);
+    }
+
+    if let Ok(chain) = state.chain_id().chain().as_str().try_into() {
+        headers.insert(X_IOTA_CHAIN, chain);
+    }
+
+    if let Ok(latest_checkpoint) = state.reader.inner().get_latest_checkpoint() {
+        headers.insert(X_IOTA_EPOCH, latest_checkpoint.epoch().into());
+        headers.insert(
+            X_IOTA_CHECKPOINT_HEIGHT,
+            latest_checkpoint.sequence_number.into(),
+        );
+        headers.insert(X_IOTA_TIMESTAMP_MS, latest_checkpoint.timestamp_ms.into());
+    }
+
+    if let Ok(lowest_available_checkpoint) = state.reader.inner().get_lowest_available_checkpoint()
+    {
+        headers.insert(
+            X_IOTA_LOWEST_AVAILABLE_CHECKPOINT,
+            lowest_available_checkpoint.into(),
+        );
+    }
 
-    let lowest_available_checkpoint_objects = state
+    if let Ok(lowest_available_checkpoint_objects) = state
         .reader
         .inner()
         .get_lowest_available_checkpoint_objects()
-        .unwrap();
-
-    let mut headers = HeaderMap::new();
-
-    headers.insert(
-        X_IOTA_CHAIN_ID,
-        state.chain_id().to_string().try_into().unwrap(),
-    );
-    headers.insert(
-        X_IOTA_CHAIN,
-        state.chain_id().chain().as_str().try_into().unwrap(),
-    );
-    headers.insert(
-        X_IOTA_EPOCH,
-        latest_checkpoint.epoch().to_string().try_into().unwrap(),
-    );
-    headers.insert(
-        X_IOTA_CHECKPOINT_HEIGHT,
-        latest_checkpoint
-            .sequence_number()
-            .to_string()
-            .try_into()
-            .unwrap(),
-    );
-    headers.insert(
-        X_IOTA_TIMESTAMP_MS,
-        latest_checkpoint
-            .timestamp_ms
-            .to_string()
-            .try_into()
-            .unwrap(),
-    );
-    headers.insert(
-        X_IOTA_LOWEST_AVAILABLE_CHECKPOINT,
-        lowest_available_checkpoint.to_string().try_into().unwrap(),
-    );
-
-    headers.insert(
-        X_IOTA_LOWEST_AVAILABLE_CHECKPOINT_OBJECTS,
-        lowest_available_checkpoint_objects
-            .to_string()
-            .try_into()
-            .unwrap(),
-    );
+    {
+        headers.insert(
+            X_IOTA_LOWEST_AVAILABLE_CHECKPOINT_OBJECTS,
+            lowest_available_checkpoint_objects.into(),
+        );
+    }
 
     (headers, response)
 }
```
