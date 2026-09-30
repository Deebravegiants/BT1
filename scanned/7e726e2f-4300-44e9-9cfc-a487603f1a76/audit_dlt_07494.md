# [?] fix(client-wasm): reject instead of panicking in RpcHandler::new

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-24
Source: https://github.com/fedimint/fedimint/commit/c10fe9ee5a2cb7159e61228fc9e11a489c3d55a2
Type: security-commit

## Details
fix(client-wasm): reject instead of panicking in RpcHandler::new

Opening the database and binding the connectors are genuinely fallible
(corrupt redb file, OPFS I/O error, quota), and a panic in an async
wasm-bindgen export leaves the returned `Promise` unsettled forever:
even with the panic hook installed the caller hangs without a
rejection it could catch. Return the errors as `JsError` so the SDK
gets a catchable exception carrying the failure reason.

wasm-bindgen's deprecation warning about async constructors remains:
fixing it means replacing the constructor with a static factory, which
changes the JS API and is left for a follow-up.

Assisted-by: Claude Fable 5 (claude-fable-5)

## Patch
### fedimint-client-wasm/src/lib.rs
```diff
@@ -42,18 +42,21 @@ struct RpcHandler {
 #[wasm_bindgen]
 impl RpcHandler {
     #[wasm_bindgen(constructor)]
-    pub async fn new(sync_handle: FileSystemSyncAccessHandle) -> Self {
-        // Create the database directly
-        let cursed_db = MemAndRedb::new(sync_handle).unwrap();
+    pub async fn new(sync_handle: FileSystemSyncAccessHandle) -> Result<RpcHandler, JsError> {
+        // Return errors instead of panicking: a panic in an async export
+        // leaves the returned `Promise` unsettled forever, so the caller
+        // would hang instead of getting a rejection it can catch.
+        let cursed_db = MemAndRedb::new(sync_handle)
+            .map_err(|err| JsError::new(&format!("Failed to open client database: {err:#}")))?;
         let database = Database::new(cursed_db, Default::default());
         let connectors = fedimint_connectors::ConnectorRegistry::build_from_client_defaults()
             .bind()
             .await
-            .unwrap();
+            .map_err(|err| JsError::new(&format!("Failed to bind client connectors: {err:#}")))?;
 
         let state = Arc::new(RpcGlobalState::new(connectors, database));
 
-        Self { state }
+        Ok(Self { state })
     }
 
     #[wasm_bindgen]
```
