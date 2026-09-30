# [?] rust: bump imbl-sized-chunks to fix RUSTSEC-2026-0292 (#22962)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-09-21
Source: https://github.com/ethereum-optimism/optimism/commit/165e2ba646c1958e3b87f0e8c55706b4b203d263
Type: security-commit

## Details
rust: bump imbl-sized-chunks to fix RUSTSEC-2026-0292 (#22962)

Co-authored-by: Claude Fable 5.1 <noreply@anthropic.com>

## Patch
### rust/Cargo.lock
```diff
@@ -2661,12 +2661,6 @@ dependencies = [
  "serde_core",
 ]
 
-[[package]]
-name = "bitmaps"
-version = "3.2.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a1d084b0137aaa901caf9f1e8b21daa6aa24d41cd806e111335541eff9683bd6"
-
 [[package]]
 name = "bitvec"
 version = "1.0.1"
@@ -6166,13 +6160,13 @@ dependencies = [
 
 [[package]]
 name = "imbl"
-version = "7.0.0"
+version = "7.0.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e525189e5f603908d0c6e0d402cb5de9c4b2c8866151fabc4ebd771ed2630a2e"
+checksum = "46bad832b9b463ed9398b8506488cc2e3b897a9d44f13af115f382aac71f4fec"
 dependencies = [
  "arbitrary",
  "archery",
- "bitmaps",
+ "equivalent",
  "imbl-sized-chunks",
  "rand_core 0.9.5",
  "rand_xoshiro",
@@ -6183,12 +6177,9 @@ dependencies = [
 
 [[package]]
 name = "imbl-sized-chunks"
-version = "0.1.3"
+version = "0.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8f4241005618a62f8d57b2febd02510fb96e0137304728543dfc5fd6f052c22d"
-dependencies = [
- "bitmaps",
-]
+checksum = "2a0813be332553f857953298749fa19549e8b61b80589757c29b4e2a804fa9c6"
 
 [[package]]
 name = "impl-codec"
```

### rust/deny.toml
```diff
@@ -28,9 +28,6 @@ ignore = [
   "RUSTSEC-2024-0384",
   # rustls-pemfile is unmaintained; transitive via tonic in the SP1 dependency tree.
   "RUSTSEC-2025-0134",
-  # bitmaps is unmaintained (repository archived, no patched release exists).
-  # Transitive via imbl -> reth-transaction-pool. Pending upstream dropping imbl.
-  "RUSTSEC-2026-0247",
 ]
 
 # This section is considered when running `cargo deny check bans`.
```
