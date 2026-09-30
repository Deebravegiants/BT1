# [?] fix: cargo audit issue RUSTSEC-2025-0014 (#5723)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2025-03-11
Source: https://github.com/chainflip-io/chainflip-backend/commit/94b712dbf6f6907454b09b9ebd831ea3a8281544
Type: security-commit

## Details
fix: cargo audit issue RUSTSEC-2025-0014 (#5723)

## Patch
### .cargo/config.toml
```diff
@@ -48,6 +48,7 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2025-0009: Transitive dependency use by rustls 0.20.9, as per the advisory, TLS is unaffected.
 # - RUSTSEC-2025-0010: Transitive dependency use by rustls 0.20.9, as per the advisory, TLS is unaffected.
 # - RUSTSEC-2024-0436: Paste is no longer maintained. This is a pre-processor macro, so not an immediate security concern.
+# - RUSTSEC-2025-0014: Humantime is no longer maintained. Transitive dependency of `env_logger`.
 cf-audit = '''
 audit -D unmaintained -D unsound
     --ignore RUSTSEC-2021-0139
@@ -64,4 +65,5 @@ audit -D unmaintained -D unsound
     --ignore RUSTSEC-2025-0009
     --ignore RUSTSEC-2025-0010
     --ignore RUSTSEC-2024-0436
+    --ignore RUSTSEC-2025-0014
 '''
```

### Cargo.lock
```diff
@@ -3484,7 +3484,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "33d852cb9b869c2a9b3df2f71a3074817f01e1844f839a144f5fcef059a4eb5d"
 dependencies = [
  "libc",
- "windows-sys 0.59.0",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -6217,7 +6217,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "fc2f4eb4bc735547cfed7c0a4922cbd04a4655978c09b54f1f7b228750664c34"
 dependencies = [
  "cfg-if",
- "windows-targets 0.52.6",
+ "windows-targets 0.48.5",
 ]
 
 [[package]]
@@ -10235,7 +10235,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys 0.4.15",
- "windows-sys 0.59.0",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -14192,7 +14192,7 @@ dependencies = [
  "getrandom 0.2.15",
  "once_cell",
  "rustix 0.38.43",
- "windows-sys 0.59.0",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -15772,7 +15772,7 @@ version = "0.1.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "cf221c93e13a30d793f7645a0e7762c55d169dbb0a49671918a2319d289b10bb"
 dependencies = [
- "windows-sys 0.59.0",
+ "windows-sys 0.48.0",
 ]
 
 [[package]]
```
