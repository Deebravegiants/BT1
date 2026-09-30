# [?] fix(libzkp): upgrade libzkp to `v0.9.2` (fix ccc panic CodeNotFound) (#520)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2023-09-19
Source: https://github.com/scroll-tech/go-ethereum/commit/fa0be69a3fb9448765dcaae8cb73bf99953a417e
Type: security-commit

## Details
fix(libzkp): upgrade libzkp to `v0.9.2` (fix ccc panic CodeNotFound) (#520)

Upgrade libzkp to `v0.9.2` (fix ccc bug).

## Patch
### params/version.go
```diff
@@ -24,7 +24,7 @@ import (
 const (
 	VersionMajor = 4         // Major version component of the current release
 	VersionMinor = 4         // Minor version component of the current release
-	VersionPatch = 10        // Patch version component of the current release
+	VersionPatch = 11        // Patch version component of the current release
 	VersionMeta  = "sepolia" // Version metadata to append to the version string
 )
 
```

### rollup/circuitcapacitychecker/libzkp/Cargo.lock
```diff
@@ -16,7 +16,7 @@ dependencies = [
 [[package]]
 name = "aggregator"
 version = "0.1.0"
-source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.1#88414cc46913978325efd744536c4d5a4a02a766"
+source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.2#2723b82fb5d538d6fcc7b2dd0d84d3df8818499f"
 dependencies = [
  "ark-std",
  "env_logger 0.10.0",
@@ -297,7 +297,7 @@ checksum = "3c6ed94e98ecff0c12dd1b04c15ec0d7d9458ca8fe806cea6f12954efe74c63b"
 [[package]]
 name = "bus-mapping"
 version = "0.1.0"
-source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.1#88414cc46913978325efd744536c4d5a4a02a766"
+source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.2#2723b82fb5d538d6fcc7b2dd0d84d3df8818499f"
 dependencies = [
  "eth-types",
  "ethers-core",
@@ -971,7 +971,7 @@ dependencies = [
 [[package]]
 name = "eth-types"
 version = "0.1.0"
-source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.1#88414cc46913978325efd744536c4d5a4a02a766"
+source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.2#2723b82fb5d538d6fcc7b2dd0d84d3df8818499f"
 dependencies = [
  "ethers-core",
  "ethers-signers",
@@ -1128,7 +1128,7 @@ dependencies = [
 [[package]]
 name = "external-tracer"
 version = "0.1.0"
-source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.1#88414cc46913978325efd744536c4d5a4a02a766"
+source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.2#2723b82fb5d538d6fcc7b2dd0d84d3df8818499f"
 dependencies = [
  "eth-types",
  "geth-utils",
@@ -1308,7 +1308,7 @@ dependencies = [
 [[package]]
 name = "gadgets"
 version = "0.1.0"
-source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.1#88414cc46913978325efd744536c4d5a4a02a766"
+source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.2#2723b82fb5d538d6fcc7b2dd0d84d3df8818499f"
 dependencies = [
  "digest 0.7.6",
  "eth-types",
@@ -1340,7 +1340,7 @@ dependencies = [
 [[package]]
 name = "geth-utils"
 version = "0.1.0"
-source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.1#88414cc46913978325efd744536c4d5a4a02a766"
+source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.2#2723b82fb5d538d6fcc7b2dd0d84d3df8818499f"
 dependencies = [
  "env_logger 0.9.3",
  "gobuild 0.1.0-alpha.2 (git+https://github.com/scroll-tech/gobuild.git)",
@@ -1949,7 +1949,7 @@ dependencies = [
 [[package]]
 name = "keccak256"
 version = "0.1.0"
-source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.1#88414cc46913978325efd744536c4d5a4a02a766"
+source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.2#2723b82fb5d538d6fcc7b2dd0d84d3df8818499f"
 dependencies = [
  "env_logger 0.9.3",
  "eth-types",
@@ -2157,7 +2157,7 @@ dependencies = [
 [[package]]
 name = "mock"
 version = "0.1.0"
-source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.1#88414cc46913978325efd744536c4d5a4a02a766"
+source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.2#2723b82fb5d538d6fcc7b2dd0d84d3df8818499f"
 dependencies = [
  "eth-types",
  "ethers-core",
@@ -2173,7 +2173,7 @@ dependencies = [
 [[package]]
 name = "mpt-zktrie"
 version = "0.1.0"
-source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.1#88414cc46913978325efd744536c4d5a4a02a766"
+source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.2#2723b82fb5d538d6fcc7b2dd0d84d3df8818499f"
 dependencies = [
  "eth-types",
  "halo2-mpt-circuits",
@@ -2595,7 +2595,7 @@ dependencies = [
 [[package]]
 name = "prover"
 version = "0.1.0"
-source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.1#88414cc46913978325efd744536c4d5a4a02a766"
+source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.2#2723b82fb5d538d6fcc7b2dd0d84d3df8818499f"
 dependencies = [
  "aggregator",
  "anyhow",
@@ -4212,7 +4212,7 @@ checksum = "2a0956f1ba7c7909bfb66c2e9e4124ab6f6482560f6628b5aaeba39207c9aad9"
 [[package]]
 name = "zkevm-circuits"
 version = "0.1.0"
-source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.1#88414cc46913978325efd744536c4d5a4a02a766"
+source = "git+https://github.com/scroll-tech/zkevm-circuits.git?tag=v0.9.2#2723b82fb5d538d6fcc7b2dd0d84d3df8818499f"
 dependencies = [
  "array-init",
  "bus-mapping",
```

### rollup/circuitcapacitychecker/libzkp/Cargo.toml
```diff
@@ -20,7 +20,7 @@ maingate = { git = "https://github.com/scroll-tech/halo2wrong", branch = "halo2-
 halo2curves = { git = "https://github.com/scroll-tech/halo2curves.git", branch = "0.3.1-derive-serde" }
 
 [dependencies]
-prover = { git = "https://github.com/scroll-tech/zkevm-circuits.git", tag = "v0.9.1", default-features = false, features = ["parallel_syn", "scroll", "shanghai"] }
+prover = { git = "https://github.com/scroll-tech/zkevm-circuits.git", tag = "v0.9.2", default-features = false, features = ["parallel_syn", "scroll", "shanghai"] }
 
 anyhow = "1.0"
 log = "0.4"
```
