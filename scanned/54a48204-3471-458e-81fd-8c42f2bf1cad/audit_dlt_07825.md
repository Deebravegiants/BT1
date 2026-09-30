# [?] Bump `h2` for RUSTSEC-2024-0332 (#5514)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2024-04-04
Source: https://github.com/sigp/lighthouse/commit/7825af4a6e38432840dcd572c4a2716a4db663e8
Type: security-commit

## Details
Bump `h2` for RUSTSEC-2024-0332 (#5514)

* Bump `h2` for RUSTSEC-2024-0332

## Patch
### Cargo.lock
```diff
@@ -3353,9 +3353,9 @@ dependencies = [
 
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
@@ -3372,9 +3372,9 @@ dependencies = [
 
 [[package]]
 name = "h2"
-version = "0.4.2"
+version = "0.4.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "31d030e59af851932b72ceebadf4a2b5986dba4c3b99dd2493f8273a0f151943"
+checksum = "816ec7294445779408f36fe57bc5b7fc1cf59664059096c65f905c1c61f58069"
 dependencies = [
  "bytes",
  "fnv",
@@ -3786,14 +3786,14 @@ dependencies = [
  "futures-channel",
  "futures-core",
  "futures-util",
- "h2 0.3.24",
+ "h2 0.3.26",
  "http 0.2.11",
  "http-body 0.4.6",
  "httparse",
  "httpdate",
  "itoa",
  "pin-project-lite",
- "socket2 0.5.6",
+ "socket2 0.4.10",
  "tokio",
  "tower-service",
  "tracing",
@@ -3809,7 +3809,7 @@ dependencies = [
  "bytes",
  "futures-channel",
  "futures-util",
- "h2 0.4.2",
+ "h2 0.4.4",
  "http 1.0.0",
  "http-body 1.0.0",
  "httparse",
@@ -6743,7 +6743,7 @@ dependencies = [
  "encoding_rs",
  "futures-core",
  "futures-util",
- "h2 0.3.24",
+ "h2 0.3.26",
  "http 0.2.11",
  "http-body 0.4.6",
  "hyper 0.14.28",
```
