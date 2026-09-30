# [?] chore(rust): patch RUSTSEC-2026-0104 in rustls-webpki (#20235)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-04-22
Source: https://github.com/ethereum-optimism/optimism/commit/b2119af4daa3a44206a72cfdf240f49e33ea5ed5
Type: security-commit

## Details
chore(rust): patch RUSTSEC-2026-0104 in rustls-webpki (#20235)

Bump rustls-webpki 0.103.12 -> 0.103.13 to fix a reachable panic when
parsing certificate revocation lists. Also drop the stale
RUSTSEC-2026-0097 ignore entry, which no longer matches any crate.

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### rust/Cargo.lock
```diff
@@ -12979,9 +12979,9 @@ checksum = "f87165f0995f63a9fbeea62b64d10b4d9d8e78ec6d7d51fb2125fda7bb36788f"
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.12"
+version = "0.103.13"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8279bb85272c9f10811ae6a6c547ff594d6a7f3c6c6b02ee9726d1d0dcfcdd06"
+checksum = "61c429a8649f110dddef65e2a5ad240f747e85f7758a6bccc7e5777bd33f756e"
 dependencies = [
  "aws-lc-rs",
  "ring",
```

### rust/deny.toml
```diff
@@ -14,8 +14,6 @@ ignore = [
   "RUSTSEC-2024-0436",
   # bincode is unmaintained but still functional; transitive dep from reth-nippy-jar and test-fuzz.
   "RUSTSEC-2025-0141",
-  # rand is unsound with a custom logger using `rand::rng()`
-  "RUSTSEC-2026-0097",
 ]
 
 # This section is considered when running `cargo deny check bans`.
```
