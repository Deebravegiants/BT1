# [?] Fix RUSTSEC-2023-0044 warning

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2023-06-21
Source: https://github.com/nervosnetwork/ckb/commit/0501ce7b6edfbe732be787b41156348dedd9a73e
Type: security-commit

## Details
Fix RUSTSEC-2023-0044 warning

Signed-off-by: Eval EXEC <execvy@gmail.com>

## Patch
### Cargo.lock
```diff
@@ -3277,9 +3277,9 @@ checksum = "624a8340c38c1b80fd549087862da4ba43e08858af025b236e509b6649fc13d5"
 
 [[package]]
 name = "openssl"
-version = "0.10.48"
+version = "0.10.55"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "518915b97df115dd36109bfa429a48b8f737bd05508cf9588977b599648926d2"
+checksum = "345df152bc43501c5eb9e4654ff05f794effb78d4efe3d53abc158baddc0703d"
 dependencies = [
  "bitflags",
  "cfg-if 1.0.0",
@@ -3309,11 +3309,10 @@ checksum = "ff011a302c396a5197692431fc1948019154afc178baf7d8e37367442a4601cf"
 
 [[package]]
 name = "openssl-sys"
-version = "0.9.83"
+version = "0.9.90"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "666416d899cf077260dac8698d60a60b435a46d57e82acb1be3d0dad87284e5b"
+checksum = "374533b0e45f3a7ced10fcaeccca020e66656bc03dac384f852e4e5a7a8104a6"
 dependencies = [
- "autocfg",
  "cc",
  "libc",
  "pkg-config",
```
