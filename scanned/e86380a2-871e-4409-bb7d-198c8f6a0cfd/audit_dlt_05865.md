# [?] chore(rust): remove stale RUSTSEC-2026-0002 ignore (#19598)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-03-17
Source: https://github.com/ethereum-optimism/optimism/commit/9cb57b0a8e3646c5a10eaa0c0c817c9765a54706
Type: security-commit

## Details
chore(rust): remove stale RUSTSEC-2026-0002 ignore (#19598)

* chore(rust): remove stale RUSTSEC-2026-0002 ignore from deny.toml

The lru crate advisory (RUSTSEC-2026-0002) no longer matches any crate
in the dependency tree, causing cargo-deny to fail with
"advisory was not encountered". The vulnerable lru versions (0.9.0–0.16.2)
have been patched — lru 0.16.3 is already in Cargo.lock.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* chore: Update lz4_flex to 0.12.1

lz4_flex 0.12.0 suffers from RUSTSEC-2026-0041

https://rustsec.org/advisories/RUSTSEC-2026-0041

---------

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
Co-authored-by: wwared <541936+wwared@users.noreply.github.com>

## Patch
### rust/Cargo.lock
```diff
@@ -6955,9 +6955,9 @@ dependencies = [
 
 [[package]]
 name = "lz4_flex"
-version = "0.12.0"
+version = "0.12.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ab6473172471198271ff72e9379150e9dfd70d8e533e0752a27e515b48dd375e"
+checksum = "98c23545df7ecf1b16c303910a69b079e8e251d60f7dd2cc9b4177f2afaf1746"
 
 [[package]]
 name = "mach2"
```

### rust/deny.toml
```diff
@@ -17,8 +17,6 @@ ignore = [
   "RUSTSEC-2025-0012",
   # bincode is unmaintained but still functional; transitive dep from reth-nippy-jar and test-fuzz.
   "RUSTSEC-2025-0141",
-  # https://rustsec.org/advisories/RUSTSEC-2026-0002 lru unused directly: https://github.com/alloy-rs/alloy/pull/3460
-  "RUSTSEC-2026-0002",
 ]
 
 # This section is considered when running `cargo deny check bans`.
```
