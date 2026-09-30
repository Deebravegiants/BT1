# [?] Address cargo audit failure `RUSTSEC-2025-0006` (#6972)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2025-02-11
Source: https://github.com/sigp/lighthouse/commit/0728140086c422a6a46a3b90a22f1145cccfd72e
Type: security-commit

## Details
Address cargo audit failure `RUSTSEC-2025-0006` (#6972)

PR to fix cargo audit failure and bump `hickory-proto` version:
https://github.com/sigp/lighthouse/actions/runs/13252660830/job/36993664960

## Patch
### Cargo.lock
```diff
@@ -1963,7 +1963,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "1145d32e826a7748b69ee8fc62d3e6355ff7f1051df53141e7048162fc90481b"
 dependencies = [
  "data-encoding",
- "syn 2.0.98",
+ "syn 1.0.109",
 ]
 
 [[package]]
@@ -3865,9 +3865,9 @@ checksum = "b07f60793ff0a4d9cef0f18e63b5357e06209987153a64648c972c1e5aff336f"
 
 [[package]]
 name = "hickory-proto"
-version = "0.25.0-alpha.4"
+version = "0.25.0-alpha.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d063c0692ee669aa6d261988aa19ca5510f1cc40e4f211024f50c888499a35d7"
+checksum = "1d00147af6310f4392a31680db52a3ed45a2e0f68eb18e8c3fe5537ecc96d9e2"
 dependencies = [
  "async-recursion",
  "async-trait",
@@ -3880,7 +3880,7 @@ dependencies = [
  "idna",
  "ipnet",
  "once_cell",
- "rand 0.8.5",
+ "rand 0.9.0",
  "socket2",
  "thiserror 2.0.11",
  "tinyvec",
@@ -4905,7 +4905,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "fc2f4eb4bc735547cfed7c0a4922cbd04a4655978c09b54f1f7b228750664c34"
 dependencies = [
  "cfg-if",
- "windows-targets 0.52.6",
+ "windows-targets 0.48.5",
 ]
 
 [[package]]
```
