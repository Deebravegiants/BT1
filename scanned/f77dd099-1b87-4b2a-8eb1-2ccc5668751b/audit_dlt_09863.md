# [?] fix: Fix `RUSTSEC-2025-0047` by updating `slab` (#8193)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-08-14
Source: https://github.com/iotaledger/iota/commit/3b86044fb042c97070efca655f034f6a03ff0dc0
Type: security-commit

## Details
fix: Fix `RUSTSEC-2025-0047` by updating `slab` (#8193)

# Description of change

Fixes https://rustsec.org/advisories/RUSTSEC-2025-0047 by updating the
`slab` dependency.

## Patch
### Cargo.lock
```diff
@@ -13230,12 +13230,9 @@ dependencies = [
 
 [[package]]
 name = "slab"
-version = "0.4.9"
+version = "0.4.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8f92a496fb766b417c996b9c5e57daf2f7ad3b0bebe1ccfca4856390e3d3bb67"
-dependencies = [
- "autocfg",
-]
+checksum = "7a2ae44ef20feb57a68b23d846850f861394c2e02dc425a50098ae8c90267589"
 
 [[package]]
 name = "slip10_ed25519"
```

### deny.toml
```diff
@@ -55,10 +55,6 @@ ignore = [
   "RUSTSEC-2024-0436",
   # backoff is unmaintained
   "RUSTSEC-2025-0012",
-  # ring 0.16 is unmaintained
-  "RUSTSEC-2025-0010",
-  # ethers uses ring 0.16
-  "RUSTSEC-2025-0009",
 ]
 # Threshold for security vulnerabilities, any vulnerability with a CVSS score
 # lower than the range specified will be ignored. Note that ignored advisories
```

### external-crates/move/Cargo.lock
```diff
@@ -3430,9 +3430,9 @@ dependencies = [
 
 [[package]]
 name = "slab"
-version = "0.4.10"
+version = "0.4.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "04dc19736151f35336d325007ac991178d504a119863a2fcb3758cdb5e52c50d"
+checksum = "7a2ae44ef20feb57a68b23d846850f861394c2e02dc425a50098ae8c90267589"
 
 [[package]]
 name = "smallvec"
```
