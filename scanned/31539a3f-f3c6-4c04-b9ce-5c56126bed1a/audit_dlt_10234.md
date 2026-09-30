# [?] pruntime: Fix crash due to HTTP ABI incompatibility

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2023-07-19
Source: https://github.com/Phala-Network/phala-blockchain/commit/9b7259be725fc5c7cba2e71cb63d9fb680b1f99c
Type: security-commit

## Details
pruntime: Fix crash due to HTTP ABI incompatibility

## Patch
### Cargo.lock
```diff
@@ -8780,7 +8780,7 @@ dependencies = [
 
 [[package]]
 name = "pink-subrpc"
-version = "0.4.2"
+version = "0.4.3"
 dependencies = [
  "base58",
  "hex",
```

### crates/pink/pink-extension-runtime/src/lib.rs
```diff
@@ -71,7 +71,26 @@ pub fn http_request(
     request: HttpRequest,
     timeout_ms: u64,
 ) -> Result<HttpResponse, HttpRequestError> {
-    block_on(async_http_request(request, timeout_ms))
+    use HttpRequestError::*;
+    match block_on(async_http_request(request, timeout_ms)) {
+        Ok(resp) => Ok(resp),
+        Err(err) => match err {
+            // runtime v1.0 supported errors
+            InvalidUrl | InvalidMethod | InvalidHeaderName | InvalidHeaderValue
+            | FailedToCreateClient | Timeout => Err(err),
+            _ => {
+                // To be compatible with runtime v1.0, we need to convert the v1.1 extended errors
+                // to an HTTP response with status code 524.
+                log::error!("chain_ext: http request failed: {}", err.display());
+                Ok(HttpResponse {
+                    status_code: 524,
+                    reason_phrase: "IO Error".into(),
+                    body: format!("{err:?}").into_bytes(),
+                    headers: vec![],
+                })
+            }
+        },
+    }
 }
 
 async fn async_http_request(
```
