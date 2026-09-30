# [?] Ignore RUSTSEC-2022-0040 - `owning_ref` soundness (#3415)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2022-08-02
Source: https://github.com/sigp/lighthouse/commit/553a7949942b74df45357e0a699c1e3006252326
Type: security-commit

## Details
Ignore RUSTSEC-2022-0040 - `owning_ref` soundness (#3415)

## Issue Addressed

NA

## Proposed Changes

We are unaffected by this issue: https://github.com/sigp/lighthouse/pull/3410#issuecomment-1203244792

## Additional Info

NA

## Patch
### Makefile
```diff
@@ -169,7 +169,7 @@ arbitrary-fuzz:
 # Runs cargo audit (Audit Cargo.lock files for crates with security vulnerabilities reported to the RustSec Advisory Database)
 audit:
 	cargo install --force cargo-audit
-	cargo audit --ignore RUSTSEC-2020-0071 --ignore RUSTSEC-2020-0159
+	cargo audit --ignore RUSTSEC-2020-0071 --ignore RUSTSEC-2020-0159 --ignore RUSTSEC-2022-0040
 
 # Runs `cargo vendor` to make sure dependencies can be vendored for packaging, reproducibility and archival purpose.
 vendor:
```
