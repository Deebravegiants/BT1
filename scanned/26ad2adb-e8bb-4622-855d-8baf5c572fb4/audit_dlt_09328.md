# [?] fix(evm): don't panic on short calldata (#6380)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2023-11-21
Source: https://github.com/foundry-rs/foundry/commit/9fab5bf87090b5209f4719d4bfa6005eaed0d30e
Type: security-commit

## Details
fix(evm): don't panic on short calldata (#6380)

## Patch
### crates/evm/evm/src/executors/fuzz/mod.rs
```diff
@@ -166,8 +166,11 @@ impl<'a> FuzzedExecutor<'a> {
                 let reason = reason.to_string();
                 result.reason = if reason.is_empty() { None } else { Some(reason) };
 
-                let args =
-                    func.abi_decode_input(&calldata.as_ref()[4..], false).unwrap_or_default();
+                let args = if let Some(data) = calldata.get(4..) {
+                    func.abi_decode_input(data, false).unwrap_or_default()
+                } else {
+                    vec![]
+                };
                 result.counterexample = Some(CounterExample::Single(BaseCounterExample {
                     sender: None,
                     addr: None,
```
