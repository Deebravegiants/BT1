# [?] To fix the crash of method to getting systeminfo by calling , from check_disk_space, Upgrade sysinfo library from 0.25.1 to 0.29.0 (#3894)

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2023-05-17
Source: https://github.com/starcoinorg/starcoin/commit/14d2b4c9b6d3811179f13ab3b5b6c36b50fd99b6
Type: security-commit

## Details
To fix the crash of method to getting systeminfo by calling , from check_disk_space, Upgrade sysinfo library from 0.25.1 to 0.29.0 (#3894)

## Patch
### Cargo.lock
```diff
@@ -4869,7 +4869,7 @@ dependencies = [
  "libc",
  "log 0.4.17",
  "miow 0.3.7",
- "ntapi",
+ "ntapi 0.3.7",
  "winapi 0.3.9",
 ]
 
@@ -6115,6 +6115,15 @@ dependencies = [
  "winapi 0.3.9",
 ]
 
+[[package]]
+name = "ntapi"
+version = "0.4.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "e8a3895c6391c39d7fe7ebc444a87eb2991b2a0bc718fdabd071eec617fc68e4"
+dependencies = [
+ "winapi 0.3.9",
+]
+
 [[package]]
 name = "num"
 version = "0.4.0"
@@ -11089,14 +11098,14 @@ dependencies = [
 
 [[package]]
 name = "sysinfo"
-version = "0.25.3"
+version = "0.29.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "71eb43e528fdc239f08717ec2a378fdb017dddbc3412de15fff527554591a66c"
+checksum = "02f1dc6930a439cc5d154221b5387d153f8183529b07c19aca24ea31e0a167e1"
 dependencies = [
  "cfg-if 1.0.0",
  "core-foundation-sys",
  "libc",
- "ntapi",
+ "ntapi 0.4.1",
  "once_cell",
  "rayon",
  "winapi 0.3.9",
```

### Cargo.toml
```diff
@@ -485,7 +485,7 @@ syn = { version = "1.0.107", features = [
     "visit",
     "fold",
 ] }
-sysinfo = "0.25.1"
+sysinfo = "0.29.0"
 tempfile = "3.2.0"
 test-helper = { path = "test-helper" }
 textwrap = "0.14.0"
```
