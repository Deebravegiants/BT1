# [?] node/cargo: update `mio` version to avoid RUSTSEC-2024-0019

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2024-03-07
Source: https://github.com/casper-network/casper-node/commit/aa2f7e3c7886072398af9105bb5f84f08894688d
Type: security-commit

## Details
node/cargo: update `mio` version to avoid RUSTSEC-2024-0019

Signed-off-by: Alexandru Sardan <alexandru@casperlabs.io>

## Patch
### Cargo.lock
```diff
@@ -4046,14 +4046,14 @@ dependencies = [
 
 [[package]]
 name = "mio"
-version = "0.8.6"
+version = "0.8.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5b9d9a46eff5b4ff64b45a9e316a6d1e0bc719ef429cbec4dc630684212bfdf9"
+checksum = "a4a650543ca06a924e8b371db273b2756685faae30f8487da1b56505a8f78b0c"
 dependencies = [
  "libc",
  "log",
  "wasi",
- "windows-sys 0.45.0",
+ "windows-sys 0.48.0",
 ]
 
 [[package]]
@@ -6202,7 +6202,7 @@ dependencies = [
  "autocfg",
  "bytes",
  "libc",
- "mio 0.8.6",
+ "mio 0.8.11",
  "num_cpus",
  "pin-project-lite",
  "socket2",
```
