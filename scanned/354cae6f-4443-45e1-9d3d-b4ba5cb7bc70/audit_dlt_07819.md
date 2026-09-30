# [?] Bump bytes to 1.11.1 to fix RUSTSEC-2026-0007 (#8743)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2026-02-04
Source: https://github.com/sigp/lighthouse/commit/c25a975929aff186fad967f470716abb5c740834
Type: security-commit

## Details
Bump bytes to 1.11.1 to fix RUSTSEC-2026-0007 (#8743)

## Patch
### Cargo.lock
```diff
@@ -1608,9 +1608,9 @@ checksum = "1fd0f2584146f6f2ef48085050886acf353beff7305ebd1ae69500e27c67f64b"
 
 [[package]]
 name = "bytes"
-version = "1.11.0"
+version = "1.11.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b35204fbdc0b3f4446b89fc1ac2cf84a8a68971995d0bf2e925ec7cd960f9cb3"
+checksum = "1e748733b7cbc798e1434b6ac524f0c1ff2ab456fe201501e6497c8417a4fc33"
 dependencies = [
  "serde",
 ]
@@ -3098,7 +3098,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "39cab71617ae0d63f51a36d69f866391735b51691dbda63cf6f96d042b63efeb"
 dependencies = [
  "libc",
- "windows-sys 0.59.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -4729,7 +4729,7 @@ checksum = "3640c1c38b8e4e43584d8df18be5fc6b0aa314ce6ebf51b53313d4306cca8e46"
 dependencies = [
  "hermit-abi",
  "libc",
- "windows-sys 0.59.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -6291,7 +6291,7 @@ version = "0.50.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7957b9740744892f114936ab4a57b3f487491bbeafaf8083688b16841a4240e5"
 dependencies = [
- "windows-sys 0.59.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -7199,7 +7199,7 @@ dependencies = [
  "once_cell",
  "socket2 0.6.1",
  "tracing",
- "windows-sys 0.59.0",
+ "windows-sys 0.60.2",
 ]
 
 [[package]]
@@ -7716,7 +7716,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys 0.11.0",
- "windows-sys 0.59.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -8781,7 +8781,7 @@ dependencies = [
  "getrandom 0.3.4",
  "once_cell",
  "rustix 1.1.2",
- "windows-sys 0.59.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -10132,7 +10132,7 @@ version = "0.1.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c2a7b1c03c876122aa43f3020e6c3c3ee5c05081c9a00739faf7503aeba10d22"
 dependencies = [
- "windows-sys 0.59.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
```

### Cargo.toml
```diff
@@ -116,7 +116,7 @@ bincode = "1"
 bitvec = "1"
 bls = { path = "crypto/bls" }
 byteorder = "1"
-bytes = "1"
+bytes = "1.11.1"
 # Turn off c-kzg's default features which include `blst/portable`. We can turn on blst's portable
 # feature ourselves when desired.
 c-kzg = { version = "2.1", default-features = false }
```
