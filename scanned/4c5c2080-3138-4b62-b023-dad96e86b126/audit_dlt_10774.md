# [?] Merge pull request #5533 from oasisprotocol/ptrus/fix/RUSTSEC-2024-0006

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2024-01-22
Source: https://github.com/oasisprotocol/oasis-core/commit/f678112706fffb36df83aac7fd4e0838b5e37766
Type: security-commit

## Details
Merge pull request #5533 from oasisprotocol/ptrus/fix/RUSTSEC-2024-0006

rust: bump shlex to v 1.3.0

## Patch
### .changelog/5533.internal.md
```diff
@@ -0,0 +1,4 @@
+rust: bump shlex to v 1.3.0
+
+[RUSTSEC-2024-0006](
+https://rustsec.org/advisories/RUSTSEC-2024-0006)
```

### Cargo.lock
```diff
@@ -2830,9 +2830,9 @@ dependencies = [
 
 [[package]]
 name = "shlex"
-version = "1.1.0"
+version = "1.3.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "43b2853a4d09f215c24cc5489c992ce46052d359b5109343cbafbf26bc62f8a3"
+checksum = "0fda2ff0d084019ba4d7c6f371c95d8fd75ce3524c3cb8fb653a3023f6323e64"
 
 [[package]]
 name = "signal-hook-registry"
```
