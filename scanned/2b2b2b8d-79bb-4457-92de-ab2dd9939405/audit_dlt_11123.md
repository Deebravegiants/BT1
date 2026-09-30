# [?] Fix `gix-validate` advisory (GHSA-p3hw-mv63-rf9w) (#7671)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2026-06-29
Source: https://github.com/FuelLabs/sway/commit/5a5b4079ff065406147da2db760645d20295c904
Type: security-commit

## Details
Fix `gix-validate` advisory (GHSA-p3hw-mv63-rf9w) (#7671)

## Description

This PR fixes `gix-validate` advisory
[GHSA-p3hw-mv63-rf9w](https://github.com/advisories/GHSA-p3hw-mv63-rf9w)
by bumping `gix-url` to v0.36 which is the first version compatible with
the `gix-validate` v0.11.1 which brings the actual fix. The final
resolved dependency for `gix-validate` is v0.11.2. There was no changes
in the code needed.

A failed automatic attempt to fix `GHSA-p3hw-mv63-rf9w` was done in
#7668.

## Checklist

- [x] I have linked to any relevant issues.
- [ ] I have commented my code, particularly in hard-to-understand
areas.
- [ ] I have updated the documentation where relevant (API docs, the
reference, and the Sway book).
- [ ] If my change requires substantial documentation changes, I have
[requested support from the DevRel
team](https://github.com/FuelLabs/devrel-requests/issues/new/choose)
- [ ] I have added tests that prove my fix is effective or that my
feature works.
- [ ] I have added (or requested a maintainer to add) the necessary
`Breaking*` or `New Feature` labels where relevant.
- [x] I have done my best to ensure that my PR adheres to [the Fuel Labs
Code Review
Standards](https://github.com/FuelLabs/rfcs/blob/master/text/code-standards/external-contributors.md).
- [x] I have requested a review from the relevant team or maintainers.

## Patch
### Cargo.lock
```diff
@@ -2301,12 +2301,6 @@ dependencies = [
  "regex-syntax 0.8.10",
 ]
 
-[[package]]
-name = "faster-hex"
-version = "0.9.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a2a2b11eda1d40935b26cf18f6833c526845ae8c41e58d09af6adeb6f0269183"
-
 [[package]]
 name = "fastrand"
 version = "2.4.1"
@@ -3460,32 +3454,11 @@ dependencies = [
  "url",
 ]
 
-[[package]]
-name = "gix-features"
-version = "0.38.2"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ac7045ac9fe5f9c727f38799d002a7ed3583cd777e3322a7c4b43e3cf437dc69"
-dependencies = [
- "gix-hash",
- "gix-trace",
- "libc",
-]
-
-[[package]]
-name = "gix-hash"
-version = "0.14.2"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f93d7df7366121b5018f947a04d37f034717e113dcf9ccd85c34b58e57a74d5e"
-dependencies = [
- "faster-hex",
- "thiserror 1.0.69",
-]
-
 [[package]]
 name = "gix-path"
-version = "0.10.22"
+version = "0.12.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7cb06c3e4f8eed6e24fd915fa93145e28a511f4ea0e768bae16673e05ed3f366"
+checksum = "afa6ac14cd14939ea94a496ce7460daa6511c09f5b84757e9cfc6f9c8d0f93a6"
 dependencies = [
  "bstr",
  "gix-trace",
@@ -3495,33 +3468,30 @@ dependencies = [
 
 [[package]]
 name = "gix-trace"
-version = "0.1.19"
+version = "0.1.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6f23569e55f2ffaf958617353b9734a7d52a7c19c439eeaa5e3efc217fd2270e"
+checksum = "44dc45eae785c0eb14173e0f152e6e224dcf4d45b6a6999a3aed22af541ad678"
 
 [[package]]
 name = "gix-url"
-version = "0.27.5"
+version = "0.36.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fd280c5e84fb22e128ed2a053a0daeacb6379469be6a85e3d518a0636e160c89"
+checksum = "65bb01ec69d55e82ccb7a19e264501ead4e6aac38463a8cebfdd81e22bb67ab2"
 dependencies = [
  "bstr",
- "gix-features",
  "gix-path",
- "home",
+ "percent-encoding",
  "serde",
- "thiserror 1.0.69",
- "url",
+ "thiserror 2.0.18",
 ]
 
 [[package]]
 name = "gix-validate"
-version = "0.10.1"
+version = "0.11.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5b1e63a5b516e970a594f870ed4571a8fdcb8a344e7bd407a20db8bd61dbfde4"
+checksum = "7bc6fc771c4063ba7cd2f47b91fb6076251c6a823b64b7fe7b8874b0fe4afae3"
 dependencies = [
  "bstr",
- "thiserror 2.0.18",
 ]
 
 [[package]]
```

### Cargo.toml
```diff
@@ -150,7 +150,7 @@ futures-util = "0.3"
 gag = "1.0"
 gimli = "0.31"
 git2 = "0.19"
-gix-url = "0.27"
+gix-url = "0.36"
 glob = "0.3"
 graph-cycles = "0.1"
 hashbrown = "0.14"
```
