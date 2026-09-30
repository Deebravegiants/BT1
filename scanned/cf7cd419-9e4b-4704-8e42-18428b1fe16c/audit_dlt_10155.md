# [?] ci: skip RUSTSEC-2021-0020 temporarily

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-02-07
Source: https://github.com/nervosnetwork/ckb/commit/d0c739fe1db745e01c3f8c9d3a6241527f3c3720
Type: security-commit

## Details
ci: skip RUSTSEC-2021-0020 temporarily

## Patch
### Cargo.lock
```diff
@@ -2127,7 +2127,7 @@ dependencies = [
  "futures-sink",
  "futures-task",
  "memchr",
- "pin-project 1.0.1",
+ "pin-project",
  "pin-utils",
  "proc-macro-hack",
  "proc-macro-nested",
@@ -2624,9 +2624,9 @@ dependencies = [
 
 [[package]]
 name = "hyper"
-version = "0.13.7"
+version = "0.13.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3e68a8dd9716185d9e64ea473ea6ef63529252e3e27623295a0378a19665d5eb"
+checksum = "8a6f157065790a3ed2f88679250419b5cdd96e714a0d65f7797fd337186e96bb"
 dependencies = [
  "bytes 0.5.6",
  "futures-channel",
@@ -2636,10 +2636,10 @@ dependencies = [
  "http 0.2.1",
  "http-body 0.3.1",
  "httparse",
+ "httpdate",
  "itoa",
- "pin-project 0.4.23",
+ "pin-project",
  "socket2",
- "time",
  "tokio 0.2.24",
  "tower-service",
  "tracing",
@@ -2666,7 +2666,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d979acc56dcb5b8dddba3917601745e877576475aa046df3226eabdecef78eed"
 dependencies = [
  "bytes 0.5.6",
- "hyper 0.13.7",
+ "hyper 0.13.10",
  "native-tls",
  "tokio 0.2.24",
  "tokio-tls",
@@ -3127,7 +3127,7 @@ version = "0.3.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "e14017d204ae062dc5c68a321e3dbdcd9b30181305cb6b067932f7f03f754e27"
 dependencies = [
- "hyper 0.13.7",
+ "hyper 0.13.10",
  "log",
  "metrics-core",
 ]
@@ -3753,33 +3753,13 @@ dependencies = [
  "siphasher",
 ]
 
-[[package]]
-name = "pin-project"
-version = "0.4.23"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ca4433fff2ae79342e497d9f8ee990d174071408f28f726d6d83af93e58e48aa"
-dependencies = [
- "pin-project-internal 0.4.23",
-]
-
 [[package]]
 name = "pin-project"
 version = "1.0.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "ee41d838744f60d959d7074e3afb6b35c7456d0f61cad38a24e35e6553f73841"
 dependencies = [
- "pin-project-internal 1.0.1",
-]
-
-[[package]]
-name = "pin-project-internal"
-version = "0.4.23"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2c0e815c3ee9a031fdf5af21c10aa17c573c9c6a566328d99e3936c34e36461f"
-dependencies = [
- "proc-macro2",
- "quote",
- "syn",
+ "pin-project-internal",
 ]
 
 [[package]]
@@ -4231,7 +4211,7 @@ dependencies = [
  "futures-util",
  "http 0.2.1",
  "http-body 0.3.1",
- "hyper 0.13.7",
+ "hyper 0.13.10",
  "hyper-tls 0.4.3",
  "ipnet",
  "js-sys",
```

### deny.toml
```diff
@@ -8,6 +8,7 @@ ignore = [
     "RUSTSEC-2020-0082", # TODO ordered_float:NotNan may contain NaN after panic in assignment operators
                          #      Could be removed after heim 0.1.0 released.
     "RUSTSEC-2021-0013", # TODO We did not use heim-virt to get cpu information
+    "RUSTSEC-2021-0020", # TODO JsonRPC unable to upgrade, considering that the trigger condition is too harsh(upstream proxy and proxy is wrong), ignore it for now
 ]
 
 [licenses]
```
