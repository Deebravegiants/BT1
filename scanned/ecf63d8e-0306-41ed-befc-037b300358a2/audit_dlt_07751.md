# [?] fix: Bearer token parsing vulnerability  (#18712)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2025-09-25
Source: https://github.com/paradigmxyz/reth/commit/aa192c255b53335ba509987c82ab26e79e954195
Type: security-commit

## Details
fix: Bearer token parsing vulnerability  (#18712)

## Patch
### crates/rpc/rpc-layer/src/jwt_validator.rs
```diff
@@ -47,8 +47,12 @@ fn get_bearer(headers: &HeaderMap) -> Option<String> {
     let header = headers.get(header::AUTHORIZATION)?;
     let auth: &str = header.to_str().ok()?;
     let prefix = "Bearer ";
-    let index = auth.find(prefix)?;
-    let token: &str = &auth[index + prefix.len()..];
+
+    if !auth.starts_with(prefix) {
+        return None;
+    }
+
+    let token: &str = &auth[prefix.len()..];
     Some(token.into())
 }
 
@@ -93,4 +97,28 @@ mod tests {
         let token = get_bearer(&headers);
         assert!(token.is_none());
     }
+
+    #[test]
+    fn auth_header_bearer_in_middle() {
+        // Test that "Bearer " must be at the start of the header, not in the middle
+        let jwt = "valid_token";
+        let bearer = format!("NotBearer Bearer {jwt}");
+        let mut headers = HeaderMap::new();
+        headers.insert(header::AUTHORIZATION, bearer.parse().unwrap());
+        let token = get_bearer(&headers);
+        // Function should return None since "Bearer " is not at the start
+        assert!(token.is_none());
+    }
+
+    #[test]
+    fn auth_header_bearer_without_space() {
+        // Test that "BearerBearer" is not treated as "Bearer "
+        let jwt = "valid_token";
+        let bearer = format!("BearerBearer {jwt}");
+        let mut headers = HeaderMap::new();
+        headers.insert(header::AUTHORIZATION, bearer.parse().unwrap());
+        let token = get_bearer(&headers);
+        // Function should return None since header doesn't start with "Bearer "
+        assert!(token.is_none());
+    }
 }
```
