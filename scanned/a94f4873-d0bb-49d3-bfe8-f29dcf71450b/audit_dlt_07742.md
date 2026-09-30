# [?] fix(reth-bench): return error instead of panic on invalid payload (#21557)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-01-29
Source: https://github.com/paradigmxyz/reth/commit/2352158b3dc60cf8f7ce8522984fd57669d38b98
Type: security-commit

## Details
fix(reth-bench): return error instead of panic on invalid payload (#21557)

Co-authored-by: Amp <amp@ampcode.com>

## Patch
### bin/reth-bench/src/valid_payload.rs
```diff
@@ -260,7 +260,9 @@ pub(crate) async fn call_new_payload<N: Network, P: Provider<N>>(
     while !status.is_valid() {
         if status.is_invalid() {
             error!(?status, ?params, "Invalid {method}",);
-            panic!("Invalid {method}: {status:?}");
+            return Err(alloy_json_rpc::RpcError::LocalUsageError(Box::new(std::io::Error::other(
+                format!("Invalid {method}: {status:?}"),
+            ))))
         }
         if status.is_syncing() {
             return Err(alloy_json_rpc::RpcError::UnsupportedFeature(
```
