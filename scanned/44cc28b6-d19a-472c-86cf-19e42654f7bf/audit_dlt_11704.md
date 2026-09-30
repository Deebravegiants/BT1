# [?] Pin redb to GitHub revision to avoid panic (#89)

## Summary
Severity: Unknown
Chain: Bitcoin
Component: ordinals/ord
Published: 2022-02-01
Source: https://github.com/ordinals/ord/commit/994e7cf1d3ffadb4f8f64450a6bbebc2d0901a23
Type: security-commit

## Details
Pin redb to GitHub revision to avoid panic (#89)

## Patch
### Cargo.lock
```diff
@@ -230,9 +230,9 @@ checksum = "e2abad23fbc42b3700f2f279844dc832adb2b2eb069b2df918f455c4e18cc646"
 
 [[package]]
 name = "libc"
-version = "0.2.113"
+version = "0.2.116"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "eef78b64d87775463c549fbd80e19249ef436ea3bf1de2a1eb7e717ec7fab1e9"
+checksum = "565dbd88872dbe4cc8a46e527f26483c1d1f7afa6b884a3bd6cd893d4f98da74"
 
 [[package]]
 name = "log"
@@ -330,8 +330,7 @@ dependencies = [
 [[package]]
 name = "redb"
 version = "0.0.3"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4abffd54fd09d91d16ddb4cf74fd8686eccc3d45341dee6c7db1c17d8c9cd5cc"
+source = "git+https://github.com/cberner/redb.git?rev=bf905c870114f2710fbd36aefcd07b35cccfe1f7#bf905c870114f2710fbd36aefcd07b35cccfe1f7"
 dependencies = [
  "libc",
  "memmap2",
```

### Cargo.toml
```diff
@@ -15,7 +15,7 @@ executable-path = "1.0.0"
 integer-cbrt = "0.1.2"
 integer-sqrt = "0.1.5"
 log = "0.4.14"
-redb = "0.0.3"
+redb = { git = "https://github.com/cberner/redb.git", rev = "bf905c870114f2710fbd36aefcd07b35cccfe1f7" }
 structopt = "0.3.25"
 tempfile = "3.2.0"
 unindent = "0.1.7"
```
