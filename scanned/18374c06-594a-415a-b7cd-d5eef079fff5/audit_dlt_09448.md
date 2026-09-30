# [?] Merge fix/bump-spec-version into security/ghsa-2026-001-coldkey-swap-proxy-takeover

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-12
Source: https://github.com/RaoFoundation/subtensor/commit/3d0b9a2e80ad64111fc2f8a3405a65045e0d7966
Type: security-commit

## Details
Merge fix/bump-spec-version into security/ghsa-2026-001-coldkey-swap-proxy-takeover

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
