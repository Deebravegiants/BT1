# [?] fix: deadlock issue

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2025-02-13
Source: https://github.com/Conflux-Chain/conflux-rust/commit/26d1f9abf1c29788a182fe712034eb480bcc22b0
Type: security-commit

## Details
fix: deadlock issue

## Patch
### crates/cfxcore/executor/src/state/state_object/basic_fields.rs
```diff
@@ -145,6 +145,8 @@ impl State {
         let authority_code = authority_acc.code();
         let authority_code_hash = authority_acc.code_hash();
 
+        std::mem::drop(authority_acc);
+
         let (code, code_hash) = if address.space == Space::Native {
             // Core space does not support-7702
             (authority_code, authority_code_hash)
```
