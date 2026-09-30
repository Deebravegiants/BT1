# [?] Fix timeout overflow

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2023-01-12
Source: https://github.com/Phala-Network/phala-blockchain/commit/b80a49ef707ea12420e2c59f641d0f2d35a57005
Type: security-commit

## Details
Fix timeout overflow

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
