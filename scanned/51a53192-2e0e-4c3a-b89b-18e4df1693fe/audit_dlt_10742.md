# [?] chore(deps): bump imbl to 7.0.2 to fix RUSTSEC-2026-0292 (#13029)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-09-25
Source: https://github.com/iotaledger/iota/commit/cc4d63d91ce7be62e467624e07714659dc4ea78f
Type: security-commit

## Details
chore(deps): bump imbl to 7.0.2 to fix RUSTSEC-2026-0292 (#13029)

# Description of change

`cargo deny check advisories` fails on RUSTSEC-2026-0292. 
`imbl` 5.0.0 pins `imbl-sized-chunks ^0.1.3`; the patched 0.2.0 is only
reachable through `imbl` 7.0.2.

This PR:
- bump `imbl` 5.0.0 → 7.0.2 in the Move workspace
- bump `wide` 0.7.28 → 0.7.33 in the root lock: `imbl` 7 declares `wide
^0.7` but uses `u8x16::move_mask`, which the older pin lacks
- adapt `move-stackless-bytecode` to two `imbl` 7 API changes
(`ordmap::ConsumingIter<K, V, P>` generics; `Comparable` bound on
`OrdSet::contains`)
- drop the `bitmaps` advisory ignore from
`external-crates/move/deny.toml`; `imbl-sized-chunks` 0.2.0 no longer
depends on it. The root `deny.toml` keeps it because `bitmaps` 2.x still
arrives via `im` → `fastcrypto-zkp`

Upstream:
Counterpart of upstream Sui
[#27693](github.com/MystenLabs/sui/pull/27693), minus the `im` → `imbl`
migration in Sui's main crates, which IOTA never needed (`im` is not a
direct dependency here).

## Links to any relevant issues

#12987 

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [x] Patch-specific tests (correctness, functionality coverage)
- [ ] I have added tests that prove my fix is effective or that my
feature works
- [x] I have checked that new and existing unit tests pass locally with
my changes

`cargo deny check advisories` and `check bans licenses sources` pass on
both `./Cargo.toml` and `external-crates/move/Cargo.toml`.
`move-analyzer` and `move-stackless-bytecode` compile in both
workspaces; their 46 tests pass.

Co-authored-by: Claude Fable 5.1 <noreply@anthropic.com>

## Patch
### Cargo.lock
```diff
@@ -1896,12 +1896,6 @@ dependencies = [
  "typenum",
 ]
 
-[[package]]
-name = "bitmaps"
-version = "3.2.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a1d084b0137aaa901caf9f1e8b21daa6aa24d41cd806e111335541eff9683bd6"
-
 [[package]]
 name = "bitvec"
 version = "0.20.4"
@@ -3866,9 +3860,9 @@ dependencies = [
 
 [[package]]
 name = "equivalent"
-version = "1.0.1"
+version = "1.0.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5443807d6dff69373d433ab9ef5378ad8df50ca6298caf15de6e52e24aaf54d5"
+checksum = "877a4ace8713b0bcf2a4e7eec82529c029f1d0619886d18145fea96c3ffe5c0f"
 
 [[package]]
 name = "erasable"
@@ -5269,7 +5263,7 @@ version = "15.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d0acd33ff0285af998aaf9b57342af478078f53492322fafc47450e09397e0e9"
 dependencies = [
- "bitmaps 2.1.0",
+ "bitmaps",
  "rand_core 0.6.4",
  "rand_xoshiro 0.6.0",
  "sized-chunks",
@@ -5279,26 +5273,24 @@ dependencies = [
 
 [[package]]
 name = "imbl"
-version = "5.0.0"
+version = "7.0.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e4308a675e4cfc1920f36a8f4d8fb62d5533b7da106844bd1ec51c6f1fa94a0c"
+checksum = "46bad832b9b463ed9398b8506488cc2e3b897a9d44f13af115f382aac71f4fec"
 dependencies = [
  "archery",
- "bitmaps 3.2.1",
+ "equivalent",
  "imbl-sized-chunks",
  "rand_core 0.9.3",
  "rand_xoshiro 0.7.0",
  "version_check",
+ "wide",
 ]
 
 [[package]]
 name = "imbl-sized-chunks"
-version = "0.1.3"
+version = "0.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8f4241005618a62f8d57b2febd02510fb96e0137304728543dfc5fd6f052c22d"
-dependencies = [
- "bitmaps 3.2.1",
-]
+checksum = "2a0813be332553f857953298749fa19549e8b61b80589757c29b4e2a804fa9c6"
 
 [[package]]
 name = "impl-codec"
@@ -13315,7 +13307,7 @@ version = "0.6.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "16d69225bde7a69b235da73377861095455d298f2b970996eec25ddbb42b3d1e"
 dependencies = [
- "bitmaps 2.1.0",
+ "bitmaps",
  "typenum",
 ]
 
@@ -15512,9 +15504,9 @@ dependencies = [
 
 [[package]]
 name = "wide"
-version = "0.7.28"
+version = "0.7.33"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b828f995bf1e9622031f8009f8481a85406ce1f4d4588ff746d872043e855690"
+checksum = "0ce5da8ecb62bcd8ec8b7ea19f69a51275e91299be594ea5cc6ef7819e16cd03"
 dependencies = [
  "bytemuck",
  "safe_arch",
```

### deny.toml
```diff
@@ -82,10 +82,9 @@ ignore = [
   "RUSTSEC-2026-0195",
   # `im` is unmaintained and its `OrdSet` insertion is unsound, together with
   # its `bitmaps` dependency. Only reachable through `fastcrypto-zkp`; remove
-  # once that switches to `imbl`.
+  # all three once that switches to `imbl`.
   "RUSTSEC-2026-0248",
   "RUSTSEC-2026-0251",
-  # `bitmaps` is also pulled in by `imbl-sized-chunks`
   "RUSTSEC-2026-0247",
   # `clear_on_drop` is unmaintained. Only reachable through `bulletproofs`,
   # pinned by `fastcrypto`; neither has a newer release that drops it.
```

### external-crates/move/Cargo.lock
```diff
@@ -218,12 +218,6 @@ version = "2.9.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "1b8e56985ec62d17e9c1001dc89c88ecd7dc08e47eba5ec7c29c7b5eeecde967"
 
-[[package]]
-name = "bitmaps"
-version = "3.2.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a1d084b0137aaa901caf9f1e8b21daa6aa24d41cd806e111335541eff9683bd6"
-
 [[package]]
 name = "bitvec"
 version = "0.20.4"
@@ -347,6 +341,12 @@ dependencies = [
  "move-transactional-test-runner",
 ]
 
+[[package]]
+name = "bytemuck"
+version = "1.25.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "95832e849adfb21180ccb6826a99da14e5d266ae5c2e668e1602cf234f153797"
+
 [[package]]
 name = "byteorder"
 version = "1.5.0"
@@ -1427,26 +1427,24 @@ dependencies = [
 
 [[package]]
 name = "imbl"
-version = "5.0.0"
+version = "7.0.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e4308a675e4cfc1920f36a8f4d8fb62d5533b7da106844bd1ec51c6f1fa94a0c"
+checksum = "46bad832b9b463ed9398b8506488cc2e3b897a9d44f13af115f382aac71f4fec"
 dependencies = [
  "archery",
- "bitmaps",
+ "equivalent",
  "imbl-sized-chunks",
  "rand_core 0.9.5",
  "rand_xoshiro",
  "version_check",
+ "wide",
 ]
 
 [[package]]
 name = "imbl-sized-chunks"
-version = "0.1.3"
+version = "0.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8f4241005618a62f8d57b2febd02510fb96e0137304728543dfc5fd6f052c22d"
-dependencies = [
- "bitmaps",
-]
+checksum = "2a0813be332553f857953298749fa19549e8b61b80589757c29b4e2a804fa9c6"
 
 [[package]]
 name = "impl-codec"
@@ -3406,6 +3404,15 @@ version = "1.0.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "28d3b2b1366ec20994f1fd18c3c594f05c5dd4bc44d8bb0c1c632c8d6829481f"
 
+[[package]]
+name = "safe_arch"
+version = "0.7.4"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "96b02de82ddbe1b636e6170c21be622223aea188ef2e139be0a5b219ec215323"
+dependencies = [
+ "bytemuck",
+]
+
 [[package]]
 name = "same-file"
 version = "1.0.6"
@@ -4368,6 +4375,16 @@ dependencies = [
  "web-sys",
 ]
 
+[[package]]
+name = "wide"
+version = "0.7.33"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "0ce5da8ecb62bcd8ec8b7ea19f69a51275e91299be594ea5cc6ef7819e16cd03"
+dependencies = [
+ "bytemuck",
+ "safe_arch",
+]
+
 [[package]]
 name = "widestring"
 version = "0.5.1"
```

### external-crates/move/Cargo.toml
```diff
@@ -49,7 +49,7 @@ heck = "0.3.2"
 hex = "0.4.3"
 hex-literal = "0.3.4"
 hkdf = "0.10.0"
-imbl = "5.0.0"
+imbl = "7.0.2"
 indexmap = "2.11.0"
 inline_colorization = "0.1.6"
 insta = "1.42.0"
```

### external-crates/move/crates/move-stackless-bytecode/src/dataflow_domains.rs
```diff
@@ -153,7 +153,7 @@ impl<E: Ord + Clone> SetDomain<E> {
     /// Implements set difference, which is not following standard APIs for rust
     /// sets in OrdSet
     pub fn difference<'a>(&'a self, other: &'a Self) -> impl Iterator<Item = &'a E> {
-        self.iter().filter(move |e| !other.contains(e))
+        self.iter().filter(move |e| !other.contains(*e))
     }
 
     /// Implements is_disjoint which is not available in OrdSet
@@ -225,7 +225,7 @@ impl<K: Ord + Clone, V: AbstractDomain + Clone> std::iter::FromIterator<(K, V)>
 
 impl<K: Ord + Clone, V: AbstractDomain + Clone> std::iter::IntoIterator for MapDomain<K, V> {
     type Item = (K, V);
-    type IntoIter = imbl::ordmap::ConsumingIter<(K, V), DefaultSharedPtr>;
+    type IntoIter = imbl::ordmap::ConsumingIter<K, V, DefaultSharedPtr>;
     fn into_iter(self) -> Self::IntoIter {
         self.0.into_iter()
     }
```

### external-crates/move/deny.toml
```diff
@@ -51,8 +51,6 @@ ignore = [
   "RUSTSEC-2024-0384",
   # `paste` is unmaintained
   "RUSTSEC-2024-0436",
-  # `bitmaps` is unmaintained, pulled in by `imbl-sized-chunks`
-  "RUSTSEC-2026-0247",
 ]
 # Threshold for security vulnerabilities, any vulnerability with a CVSS score
 # lower than the range specified will be ignored. Note that ignored advisories
```
