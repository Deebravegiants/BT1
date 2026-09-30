# [?] Update to Go 1.15.5 to account for CVE-2020-28362

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2020-11-27
Source: https://github.com/wormhole-foundation/wormhole/commit/36a025b088db0cd02d61e7f165c483e61196c16f
Type: security-commit

## Details
Update to Go 1.15.5 to account for CVE-2020-28362

## Patch
### DEVELOP.md
```diff
@@ -4,7 +4,7 @@
 
 The following dependencies are required for local development:
 
-- [Go](https://golang.org/dl/) >= 1.15.3
+- [Go](https://golang.org/dl/) >= 1.15.5
 - [Docker](https://docs.docker.com/engine/install/) / moby-engine >= 19.03
 - [Tilt](http://tilt.dev/) >= 0.17.2
 - Any of the local Kubernetes clusters supported by Tilt. 
```

### Tiltfile
```diff
@@ -17,7 +17,7 @@
 #       +-> third_party/solana/Dockerfile <--------------+  |  |
 #                              +                            |  |    +-----------------+
 #                              +-->  solana-devnet  +-------|-----> |  solana-devnet  |
-#      golang:1.15.3                                        +-----> | [setup]         |
+#      golang:1.*                                           +-----> | [setup]         |
 #       +                                                      |    +-----------------+
 #       +-> bridge/Dockerfile   +->  guardiand-image +---------+
 #
```

### bridge/Dockerfile
```diff
@@ -1,5 +1,5 @@
 # syntax=docker/dockerfile:experimental
-FROM golang:1.15.3
+FROM golang:1.15.5
 
 WORKDIR /app
 
```

### dev-install.sh
```diff
@@ -43,7 +43,7 @@ export PATH=/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/sbin:/bin
 
 # Install Go binaries.
 ARCH=amd64
-GO=1.15.3
+GO=1.15.5
 # TODO(leo): verify checksum
 
 (
```

### docs/operations.md
```diff
@@ -49,9 +49,12 @@ Wormhole binaries from source. A Git repo is much harder to tamper with than rel
 
 To build Wormhole, you need:
 
-- [Go](https://golang.org/dl/) >= 1.15.3
+- [Go](https://golang.org/dl/) >= 1.15.5
 - [Rust](https://www.rust-lang.org/learn/get-started) >= 1.47.0
 
+It is very important to use a sufficiently recent Go version that includes a fix for
+[CVE-2020-28362](https://blog.ethereum.org/2020/11/12/geth_security_release/).
+
 If your Linux distribution has recent enough packages for these, it's preferable to use those and avoid
 the extra third-party build dependency.
 
@@ -88,7 +91,7 @@ existing build pipeline. If you need Dockerfile examples, you can take a look at
 
 To generate a guardian key, you only need to only build the Go bridge.
 
-It requires [Go](https://golang.org/dl/) >= 1.15.3. Clone the Wormhole repo
+It requires [Go](https://golang.org/dl/) >= 1.15.5. Clone the Wormhole repo
 and build the binary:
 
     git clone https://github.com/certusone/wormhole
```
