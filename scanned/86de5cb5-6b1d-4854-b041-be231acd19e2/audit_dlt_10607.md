# [?] Bump `h2` version to dodge `RUSTSEC-2024-0332`

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2024-06-20
Source: https://github.com/casper-network/casper-node/commit/1b858b3397506b8afac769c83fa82f949a434d5d
Type: security-commit

## Details
Bump `h2` version to dodge `RUSTSEC-2024-0332`

## Patch
### Cargo.lock
```diff
@@ -3033,9 +3033,9 @@ dependencies = [
 
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

### Makefile
```diff
@@ -145,7 +145,7 @@ lint-smart-contracts:
 
 .PHONY: audit-rs
 audit-rs:
-	$(CARGO) audit --ignore RUSTSEC-2024-0332 --ignore RUSTSEC-2024-0344
+	$(CARGO) audit --ignore RUSTSEC-2024-0344
 
 .PHONY: audit-as
 audit-as:
```
