# [?] fix: miner panics since the future created by hyper 0.13 need tokio 0.2 runtime

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-06-22
Source: https://github.com/nervosnetwork/ckb/commit/a07bddcb3513d589f6195f24e2ee8fb13ff443e8
Type: security-commit

## Details
fix: miner panics since the future created by hyper 0.13 need tokio 0.2 runtime

## Patch
### Cargo.lock
```diff
@@ -895,6 +895,7 @@ dependencies = [
  "serde",
  "serde_json",
  "tokio 1.7.0",
+ "tokio-compat-02",
 ]
 
 [[package]]
@@ -4835,6 +4836,20 @@ dependencies = [
  "winapi 0.3.8",
 ]
 
+[[package]]
+name = "tokio-compat-02"
+version = "0.2.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "e7d4237822b7be8fff0a7a27927462fad435dcb6650f95cea9e946bf6bdc7e07"
+dependencies = [
+ "bytes 0.5.6",
+ "once_cell",
+ "pin-project-lite 0.2.4",
+ "tokio 0.2.25",
+ "tokio 1.7.0",
+ "tokio-stream",
+]
+
 [[package]]
 name = "tokio-macros"
 version = "1.1.0"
@@ -4846,6 +4861,17 @@ dependencies = [
  "syn",
 ]
 
+[[package]]
+name = "tokio-stream"
+version = "0.1.6"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "f8864d706fdb3cc0843a49647ac892720dac98a6eeb818b77190592cf4994066"
+dependencies = [
+ "futures-core",
+ "pin-project-lite 0.2.4",
+ "tokio 1.7.0",
+]
+
 [[package]]
 name = "tokio-tls"
 version = "0.3.1"
```

### miner/Cargo.toml
```diff
@@ -33,3 +33,4 @@ eaglesong = "0.1"
 base64 = "0.13.0"
 jsonrpc-core = "17.1"
 tokio = { version = "1", features = ["sync"]  }
+tokio-compat-02 = "0.2"
```

### miner/src/client.rs
```diff
@@ -24,6 +24,7 @@ use std::convert::Into;
 use std::thread;
 use std::time;
 use tokio::sync::{mpsc, oneshot};
+use tokio_compat_02::FutureExt;
 
 type RpcRequest = (oneshot::Sender<Result<Bytes, RpcError>>, MethodCall);
 
@@ -68,6 +69,7 @@ impl Rpc {
                         }
                         let request = match client
                             .request(req)
+                            .compat()
                             .await
                             .map(|res|res.into_body())
                         {
```
