# [?] bump spec_version to 419 for the GHSA-2026-010/-011 runtime logic changes

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-16
Source: https://github.com/RaoFoundation/subtensor/commit/563e3114c4bc06ce68efee7cece6fe8d731e26b9
Type: security-commit

## Details
bump spec_version to 419 for the GHSA-2026-010/-011 runtime logic changes

## Patch
### runtime/src/lib.rs
```diff
@@ -277,7 +277,7 @@ pub const VERSION: RuntimeVersion = RuntimeVersion {
     //   `spec_version`, and `authoring_version` are the same between Wasm and native.
     // This value is set to 100 to notify Polkadot-JS App (https://polkadot.js.org/apps) to use
     //   the compatible custom types.
-    spec_version: 418,
+    spec_version: 419,
     impl_version: 1,
     apis: RUNTIME_API_VERSIONS,
     transaction_version: 1,
```
