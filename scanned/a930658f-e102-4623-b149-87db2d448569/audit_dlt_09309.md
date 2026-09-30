# [?] fix(forge): avoid etch panic on invalid bytecode (#10006)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-03-04
Source: https://github.com/foundry-rs/foundry/commit/09b0a0c075eba85324a27cf7ed2e63d829df884c
Type: security-commit

## Details
fix(forge): avoid etch panic on invalid bytecode (#10006)

## Patch
### crates/cheatcodes/src/evm.rs
```diff
@@ -516,7 +516,8 @@ impl Cheatcode for etchCall {
         let Self { target, newRuntimeBytecode } = self;
         ensure_not_precompile!(target, ccx);
         ccx.ecx.load_account(*target)?;
-        let bytecode = Bytecode::new_raw(Bytes::copy_from_slice(newRuntimeBytecode));
+        let bytecode = Bytecode::new_raw_checked(Bytes::copy_from_slice(newRuntimeBytecode))
+            .map_err(|e| fmt_err!("failed to create bytecode: {e}"))?;
         ccx.ecx.journaled_state.set_code(*target, bytecode);
         Ok(Default::default())
     }
```
