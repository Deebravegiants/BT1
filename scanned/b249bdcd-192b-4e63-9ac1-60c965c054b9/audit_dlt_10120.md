# [?] fix(deps): bump h2 to 0.4.17 (RUSTSEC-2026-0258) (#5309)

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2026-09-10
Source: https://github.com/nervosnetwork/ckb/commit/95fd03933ce2a396b84aed12caaa0f984165cd6c
Type: security-commit

## Details
fix(deps): bump h2 to 0.4.17 (RUSTSEC-2026-0258) (#5309)

@-

Co-authored-by: changshenhan <217217832+changshenhan@users.noreply.github.com>

## Patch
### Cargo.lock
```diff
@@ -2704,7 +2704,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "39cab71617ae0d63f51a36d69f866391735b51691dbda63cf6f96d042b63efeb"
 dependencies = [
  "libc",
- "windows-sys 0.61.2",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -3189,9 +3189,9 @@ dependencies = [
 
 [[package]]
 name = "h2"
-version = "0.4.13"
+version = "0.4.17"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2f44da3a8150a6703ed5d34e164b875fd14c2cdab9af1252a9a1020bde2bdc54"
+checksum = "9f877e75f39e9827ec50a572dd592684ac28c029578726c85f1b2aa6ab807449"
 dependencies = [
  "atomic-waker",
  "bytes",
@@ -3550,7 +3550,7 @@ dependencies = [
  "libc",
  "percent-encoding",
  "pin-project-lite",
- "socket2 0.6.3",
+ "socket2 0.5.10",
  "system-configuration",
  "tokio",
  "tower-service",
@@ -3881,7 +3881,7 @@ checksum = "3640c1c38b8e4e43584d8df18be5fc6b0aa314ce6ebf51b53313d4306cca8e46"
 dependencies = [
  "hermit-abi",
  "libc",
- "windows-sys 0.61.2",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -5774,7 +5774,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys 0.12.1",
- "windows-sys 0.61.2",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -6745,7 +6745,7 @@ dependencies = [
  "getrandom 0.4.2",
  "once_cell",
  "rustix 1.1.4",
- "windows-sys 0.61.2",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -7768,7 +7768,7 @@ version = "0.1.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c2a7b1c03c876122aa43f3020e6c3c3ee5c05081c9a00739faf7503aeba10d22"
 dependencies = [
- "windows-sys 0.61.2",
+ "windows-sys 0.48.0",
 ]
 
 [[package]]
```
