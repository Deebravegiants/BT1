# [?] Merge fix/eco-tests-pin-time-e0119 into security/ghsa-2026-001-coldkey-swap-proxy-takeover

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-12
Source: https://github.com/RaoFoundation/subtensor/commit/0858455d2be11ebf4b38e5b6daf5c7be4c517280
Type: security-commit

## Details
Merge fix/eco-tests-pin-time-e0119 into security/ghsa-2026-001-coldkey-swap-proxy-takeover

## Patch
### eco-tests/Cargo.toml
```diff
@@ -18,6 +18,9 @@ unwrap-used = "deny"
 useless_conversion = "allow"
 
 [dependencies]
+# Pin `time` to a version without the tracing-subscriber E0119 trait conflict that
+# breaks the eco-tests build on current stable rustc (transitive dep; eco-tests Cargo.lock is gitignored).
+time = { version = "=0.3.36", default-features = false }
 pallet-subtensor = { path = "../pallets/subtensor", default-features = false, features = ["std"] }
 pallet-alpha-assets = { path = "../pallets/alpha-assets", default-features = false, features = ["std"] }
 frame-support = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "7cc54bf2d50ae3921d718736dfeb0de9468539c7", default-features = false, features = ["std"] }
```
