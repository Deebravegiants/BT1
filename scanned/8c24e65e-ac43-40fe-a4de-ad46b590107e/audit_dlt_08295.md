# [?] bundle: fix panic on invalid server token

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-04-02
Source: https://github.com/firedancer-io/firedancer/commit/891b870e8e8cce8f9c873b51cb9a6fc5e92bafbc
Type: security-commit

## Details
bundle: fix panic on invalid server token

## Patch
### plugin/bundle/src/auth.rs
```diff
@@ -34,7 +34,9 @@ impl Interceptor for AuthInterceptor {
             "authorization",
             format!("Bearer {}", self.access_token.value)
                 .parse()
-                .unwrap(),
+                .map_err(|_| {
+                    Status::invalid_argument("Failed to parse authorization header")
+                })?,
         );
 
         Ok(request)
```
