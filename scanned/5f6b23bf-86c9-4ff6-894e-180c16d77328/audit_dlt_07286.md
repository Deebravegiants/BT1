# [?] bump h2 following RUSTSEC-2024-0332 (#10940)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-04-05
Source: https://github.com/near/nearcore/commit/f42345adb5566bd484fbcbb50a134e4e3c4590ea
Type: security-commit

## Details
bump h2 following RUSTSEC-2024-0332 (#10940)

This probably does not require a backport: the worst that could happen
is RPC nodes having (much) increased latency when under attack, under
some specific conditions.

## Patch
### Cargo.lock
```diff
@@ -2424,9 +2424,9 @@ checksum = "9b919933a397b79c37e33b77bb2aa3dc8eb6e165ad809e58ff75bc7db2e34574"
 
 [[package]]
 name = "h2"
-version = "0.3.24"
+version = "0.3.26"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bb2c4422095b67ee78da96fbb51a4cc413b3b25883c7717ff7ca1ab31022c9c9"
+checksum = "81fe527a889e1532da5c525686d96d4c2e74cdd345badf8dfef9f6b39dd5f5e8"
 dependencies = [
  "bytes",
  "fnv",
```
