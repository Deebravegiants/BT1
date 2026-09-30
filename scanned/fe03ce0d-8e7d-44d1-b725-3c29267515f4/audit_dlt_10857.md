# [?] config: Fix parse rpc address failed panic

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-06-09
Source: https://github.com/starcoinorg/starcoin/commit/4178c2e187dd75f5e12a723b028444e75b372e19
Type: security-commit

## Details
config: Fix parse rpc address failed panic

## Patch
### config/src/rpc_config.rs
```diff
@@ -114,21 +114,12 @@ impl ConfigModule for RpcConfig {
         info!("Http rpc address: {}", self.http_address.unwrap());
         self.ipc_file_path = Some(ipc_file_path);
         if let Some(rpc_address) = &opt.rpc_address {
-            self.ws_address = Some(
-                format!("{}:{}", rpc_address, DEFAULT_WEB_SOCKET_PORT)
-                    .parse::<SocketAddr>()
-                    .unwrap(),
-            );
-            self.http_address = Some(
-                format!("{}:{}", rpc_address, DEFAULT_HTTP_PORT)
-                    .parse::<SocketAddr>()
-                    .unwrap(),
-            );
-            self.tcp_address = Some(
-                format!("{}:{}", rpc_address, DEFAULT_TCP_PORT)
-                    .parse::<SocketAddr>()
-                    .unwrap(),
-            );
+            self.ws_address =
+                Some(format!("{}:{}", rpc_address, DEFAULT_WEB_SOCKET_PORT).parse::<SocketAddr>()?);
+            self.http_address =
+                Some(format!("{}:{}", rpc_address, DEFAULT_HTTP_PORT).parse::<SocketAddr>()?);
+            self.tcp_address =
+                Some(format!("{}:{}", rpc_address, DEFAULT_TCP_PORT).parse::<SocketAddr>()?);
         }
         Ok(())
     }
```
