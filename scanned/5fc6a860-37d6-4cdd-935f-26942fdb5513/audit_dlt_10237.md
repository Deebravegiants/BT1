# [?] Merge pull request #1128 from Phala-Network/fix-overflow

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2023-01-22
Source: https://github.com/Phala-Network/phala-blockchain/commit/eab9050d5af587806ffefd9e0ddd0c0c66e4b939
Type: security-commit

## Details
Merge pull request #1128 from Phala-Network/fix-overflow

Fix timeout overflow in pink runtime

## Patch
### crates/pink/pink-extension-runtime/src/lib.rs
```diff
@@ -46,11 +46,14 @@ impl<T: PinkRuntimeEnv, E: From<&'static str>> PinkExtBackend for DefaultPinkExt
     type Error = E;
     fn http_request(&self, request: HttpRequest) -> Result<HttpResponse, Self::Error> {
         // Hardcoded limitations for now
-        const MAX_QUERY_TIME: u64 = 10; // seconds
+        const MAX_QUERY_TIME: Duration = Duration::from_secs(10);
         const MAX_BODY_SIZE: usize = 1024 * 256; // 256KB
 
         let elapsed = self.env.call_elapsed().ok_or("Invalid exec env")?;
-        let timeout = Duration::from_secs(MAX_QUERY_TIME) - elapsed;
+        if elapsed >= MAX_QUERY_TIME {
+            return Err("Query time limitation exceeded".into());
+        }
+        let timeout = MAX_QUERY_TIME.saturating_sub(elapsed);
 
         let url: reqwest::Url = request.url.parse().or(Err("Invalid url"))?;
 
```
