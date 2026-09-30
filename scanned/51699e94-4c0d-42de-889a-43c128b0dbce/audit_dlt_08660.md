# [?] build: add exception for RUSTSEC-2026-0097

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkOS-test
Published: 2026-04-21
Source: https://github.com/AleoNet/snarkOS-test/commit/f1af61fe7b02257fc33f2e6c439e9facf21ed5a9
Type: security-commit

## Details
build: add exception for RUSTSEC-2026-0097

## Patch
### .cargo/audit.toml
```diff
@@ -13,4 +13,6 @@ ignore = [
   "RUSTSEC-2026-0002",
   # TODO remove once we migrate away from bincode, or it becomes maintained again.
   "RUSTSEC-2025-0141",
+  # TODO remove once termwiz/terminfo update to phf 0.13+, which drops the rand 0.8 dependency.
+  "RUSTSEC-2026-0097",
 ]
```

### Cargo.lock
```diff
@@ -157,7 +157,7 @@ version = "1.1.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "40c48f72fd53cd289104fc64099abca73db4166ad86ea0b4341abe65af83dadc"
 dependencies = [
- "windows-sys 0.61.2",
+ "windows-sys 0.60.2",
 ]
 
 [[package]]
@@ -168,7 +168,7 @@ checksum = "291e6a250ff86cd4a820112fb8898808a366d8f9f58ce16d1f538353ad55747d"
 dependencies = [
  "anstyle",
  "once_cell_polyfill",
- "windows-sys 0.61.2",
+ "windows-sys 0.60.2",
 ]
 
 [[package]]
@@ -737,7 +737,7 @@ version = "3.1.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "faf9468729b8cbcea668e36183cb69d317348c2e08e994829fb56ebfdfbaac34"
 dependencies = [
- "windows-sys 0.61.2",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -1495,7 +1495,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "39cab71617ae0d63f51a36d69f866391735b51691dbda63cf6f96d042b63efeb"
 dependencies = [
  "libc",
- "windows-sys 0.61.2",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -4092,7 +4092,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys 0.12.1",
- "windows-sys 0.61.2",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -4151,7 +4151,7 @@ dependencies = [
  "security-framework",
  "security-framework-sys",
  "webpki-root-certs",
- "windows-sys 0.61.2",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -6044,7 +6044,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "3a766e1110788c36f4fa1c2b71b387a7815aa65f88ce0229841826633d93723e"
 dependencies = [
  "libc",
- "windows-sys 0.61.2",
+ "windows-sys 0.60.2",
 ]
 
 [[package]]
@@ -6281,7 +6281,7 @@ dependencies = [
  "getrandom 0.4.2",
  "once_cell",
  "rustix 1.1.4",
- "windows-sys 0.61.2",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -7374,7 +7374,7 @@ version = "0.1.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c2a7b1c03c876122aa43f3020e6c3c3ee5c05081c9a00739faf7503aeba10d22"
 dependencies = [
- "windows-sys 0.61.2",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
```
