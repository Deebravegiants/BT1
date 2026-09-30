# [?] pink: Fix potential integer overflow

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2024-03-27
Source: https://github.com/Phala-Network/phala-blockchain/commit/c63c5954ecd574035a603a7aa293b3e527e1e156
Type: security-commit

## Details
pink: Fix potential integer overflow

## Patch
### crates/pink/chain-extension/src/lib.rs
```diff
@@ -63,7 +63,7 @@ pub fn batch_http_request(requests: Vec<HttpRequest>, timeout_ms: u64) -> ext::B
             .into_iter()
             .map(|request| async_http_request(request, timeout_ms));
         tokio::time::timeout(
-            Duration::from_millis(timeout_ms + 200),
+            Duration::from_millis(timeout_ms.saturating_add(200)),
             futures::future::join_all(futs),
         )
         .await
```
