# [?] Address cargo audit failure `RUSTSEC-2024-0437` (#7114)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2025-03-13
Source: https://github.com/sigp/lighthouse/commit/3a555f571f622979ff322290b0bf3ebd6e265489
Type: security-commit

## Details
Address cargo audit failure `RUSTSEC-2024-0437` (#7114)

Resolves #7091


  The `prometheus` crate pulls in `protobuf 2.x` which fails cargo audit. We actually dont use any `protobuf` related features in LH. By disabling default features for `prometheus`, we no longer pull in the `protobuf` crate

## Patch
### Cargo.lock
```diff
@@ -6943,7 +6943,6 @@ dependencies = [
  "lazy_static",
  "memchr",
  "parking_lot 0.12.3",
- "protobuf",
  "thiserror 1.0.69",
 ]
 
@@ -7014,12 +7013,6 @@ dependencies = [
  "types",
 ]
 
-[[package]]
-name = "protobuf"
-version = "2.28.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "106dd99e98437432fed6519dedecfade6a06a73bb7b2a1e019fdd2bee5778d94"
-
 [[package]]
 name = "psutil"
 version = "3.3.0"
```

### Cargo.toml
```diff
@@ -161,7 +161,7 @@ mockito = "1.5.0"
 num_cpus = "1"
 parking_lot = "0.12"
 paste = "1"
-prometheus = "0.13"
+prometheus = { version = "0.13", default-features = false }
 quickcheck = "1"
 quickcheck_macros = "1"
 quote = "1"
```

### Makefile
```diff
@@ -250,7 +250,7 @@ install-audit:
 	cargo install --force cargo-audit
 
 audit-CI:
-	cargo audit --ignore RUSTSEC-2024-0437
+	cargo audit
 
 # Runs `cargo vendor` to make sure dependencies can be vendored for packaging, reproducibility and archival purpose.
 vendor:
```
