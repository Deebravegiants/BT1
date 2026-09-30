# [?] fix(client): avoid port overflow when deriving websocket URLs (#4686)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2026-06-23
Source: https://github.com/otter-sec/anchor/commit/0308362192f003ce78fa0baf63152f2ade7e9878
Type: security-commit

## Details
fix(client): avoid port overflow when deriving websocket URLs (#4686)

Signed-off-by: haoshengzhen <haoshengzhen@outlook.com>

## Patch
### client/src/cluster.rs
```diff
@@ -33,8 +33,11 @@ impl FromStr for Cluster {
 
                 let mut ws_url = Url::parse(http_url)?;
                 if let Some(port) = ws_url.port() {
+                    let ws_port = port
+                        .checked_add(1)
+                        .ok_or_else(|| anyhow!("Unable to infer websocket port from {port}"))?;
                     ws_url
-                        .set_port(Some(port + 1))
+                        .set_port(Some(ws_port))
                         .map_err(|_| anyhow!("Unable to set port"))?;
                 }
                 if ws_url.scheme() == "https" {
@@ -147,6 +150,13 @@ mod tests {
             cluster
         );
     }
+
+    #[test]
+    fn test_http_max_port() {
+        let url = "http://my-url.com:65535/";
+        assert!(Cluster::from_str(url).is_err());
+    }
+
     #[test]
     fn test_https_no_port() {
         let url = "https://my-url.com/";
```
