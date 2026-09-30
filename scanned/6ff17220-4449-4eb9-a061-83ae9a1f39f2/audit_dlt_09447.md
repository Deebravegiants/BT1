# [?] Merge fix/bump-spec-version into security/ghsa-2026-002-swap-hotkey-v2-proxy-gap

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-12
Source: https://github.com/RaoFoundation/subtensor/commit/8bd31e2fe97d3d1c978c15dfd5ed81b660cbbcf8
Type: security-commit

## Details
Merge fix/bump-spec-version into security/ghsa-2026-002-swap-hotkey-v2-proxy-gap

## Patch
### runtime/src/lib.rs
```diff
@@ -277,7 +277,7 @@ pub const VERSION: RuntimeVersion = RuntimeVersion {
     //   `spec_version`, and `authoring_version` are the same between Wasm and native.
     // This value is set to 100 to notify Polkadot-JS App (https://polkadot.js.org/apps) to use
     //   the compatible custom types.
-    spec_version: 417,
+    spec_version: 418,
     impl_version: 1,
     apis: RUNTIME_API_VERSIONS,
     transaction_version: 1,
```
