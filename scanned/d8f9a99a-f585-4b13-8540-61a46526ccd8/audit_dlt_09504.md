# [?] fix: cargo audit issue RUSTSEC-2024-0442 (#5933)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2025-06-17
Source: https://github.com/chainflip-io/chainflip-backend/commit/09aeff79e0407bd1378737669576c9b3110a40a7
Type: security-commit

## Details
fix: cargo audit issue RUSTSEC-2024-0442 (#5933)

## Patch
### .cargo/config.toml
```diff
@@ -51,6 +51,7 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2025-0017: The `trust-dns` project has been rebranded to `hickory-dns`. Used by substrate.
 # - RUSTSEC-2023-0091: Low severity, difficult to exploit of wasmtime, dependency of substrate.
 # - RUSTSEC-2024-0438: Wasmtime security issue for Windows devices, so not applicable. Dependency of substrate.
+# - RUSTSEC-2024-0442: Wasmtime jit debugger issue.
 cf-audit = '''
 audit -D unmaintained -D unsound
     --ignore RUSTSEC-2021-0139
@@ -70,4 +71,5 @@ audit -D unmaintained -D unsound
     --ignore RUSTSEC-2025-0017
     --ignore RUSTSEC-2023-0091
     --ignore RUSTSEC-2024-0438
+    --ignore RUSTSEC-2024-0442
 '''
```

### Cargo.lock
```diff
@@ -2952,7 +2952,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "1145d32e826a7748b69ee8fc62d3e6355ff7f1051df53141e7048162fc90481b"
 dependencies = [
  "data-encoding",
- "syn 2.0.96",
+ "syn 1.0.109",
 ]
 
 [[package]]
@@ -3510,7 +3510,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "33d852cb9b869c2a9b3df2f71a3074817f01e1844f839a144f5fcef059a4eb5d"
 dependencies = [
  "libc",
- "windows-sys 0.59.0",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -10342,7 +10342,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys 0.4.15",
- "windows-sys 0.59.0",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -14302,7 +14302,7 @@ dependencies = [
  "getrandom 0.2.15",
  "once_cell",
  "rustix 0.38.43",
- "windows-sys 0.59.0",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -15882,7 +15882,7 @@ version = "0.1.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "cf221c93e13a30d793f7645a0e7762c55d169dbb0a49671918a2319d289b10bb"
 dependencies = [
- "windows-sys 0.59.0",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
```
