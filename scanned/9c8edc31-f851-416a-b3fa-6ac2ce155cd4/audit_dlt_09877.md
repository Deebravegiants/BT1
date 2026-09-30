# [?] chore(CI): Update diesel to 2.2.3 to avoid `RUSTSEC-2024-0365` (#2030)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2024-08-23
Source: https://github.com/iotaledger/iota/commit/fbbca22fb40aae8ebe3d196230cdf1b8c8802732
Type: security-commit

## Details
chore(CI): Update diesel to 2.2.3 to avoid `RUSTSEC-2024-0365` (#2030)

* chore(CI): Update diesel to 2.2.3 to avoid `RUSTSEC-2024-0365`

* Add cargo files to isRust

## Patch
### .github/actions/diffs/action.yml
```diff
@@ -41,6 +41,8 @@ runs:
             - ".github/workflows/_external_rust_tests.yml"
             - ".github/workflows/_external_rust_lints.yml"
             - ".github/workflows/_mysticeti_tests.yml"
+            - "Cargo.toml"
+            - "Cargo.lock"
           isDoc:
             - "docs/content/**"
             - "docs/site/**"
```

### Cargo.lock
```diff
@@ -3311,9 +3311,9 @@ dependencies = [
 
 [[package]]
 name = "diesel"
-version = "2.2.2"
+version = "2.2.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bf97ee7261bb708fa3402fa9c17a54b70e90e3cb98afb3dc8999d5512cb03f94"
+checksum = "65e13bab2796f412722112327f3e575601a3e9cdcbe426f0d30dbf43f3f5dc71"
 dependencies = [
  "bitflags 2.6.0",
  "byteorder",
@@ -7946,7 +7946,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4979f22fdb869068da03c9f7528f8297c6fd2606bc3a4affe42e6a823fdb8da4"
 dependencies = [
  "cfg-if",
- "windows-targets 0.52.6",
+ "windows-targets 0.48.5",
 ]
 
 [[package]]
@@ -10811,7 +10811,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "5bb182580f71dd070f88d01ce3de9f4da5021db7115d2e1c3605a754153b77c1"
 dependencies = [
  "bytes",
- "heck 0.5.0",
+ "heck 0.4.1",
  "itertools 0.13.0",
  "log",
  "multimap",
```
