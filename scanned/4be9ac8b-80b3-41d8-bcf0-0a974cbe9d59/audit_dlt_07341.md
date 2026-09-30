# [?] fix(sealevel): use `overflow-checks` in the release profile (#2636)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2023-08-15
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/0178eeca08e22bb7ce1709967b79eeea79608498
Type: security-commit

## Details
fix(sealevel): use `overflow-checks` in the release profile (#2636)

### Description

Uses `overflow-checks` in the release profiles of all sealevel programs
and libraries, to revert txs when this happens.

### Drive-by changes

<!--
Are there any minor or drive-by changes also included?
-->

### Related issues

- Fixes https://github.com/hyperlane-xyz/hyperlane-monorepo/issues/2590


### Backward compatibility

<!--
Are these changes backward compatible? Are there any infrastructure
implications, e.g. changes that would prohibit deploying older commits
using this infra tooling?

Yes/No
-->

### Testing

<!--
What kind of testing have these changes undergone?

None/Manual/Unit Tests
-->

## Patch
### rust/sealevel/libraries/access-control/Cargo.toml
```diff
@@ -12,3 +12,6 @@ solana-program.workspace = true
 
 [lib]
 crate-type = ["cdylib", "lib"]
+
+[profile.release]
+overflow-checks = true
```

### rust/sealevel/libraries/account-utils/Cargo.toml
```diff
@@ -14,3 +14,6 @@ spl-type-length-value.workspace = true
 
 [lib]
 crate-type = ["cdylib", "lib"]
+
+[profile.release]
+overflow-checks = true
```

### rust/sealevel/libraries/ecdsa-signature/Cargo.toml
```diff
@@ -13,3 +13,6 @@ hyperlane-core = { path = "../../../hyperlane-core" }
 
 [lib]
 crate-type = ["cdylib", "lib"]
+
+[profile.release]
+overflow-checks = true
```

### rust/sealevel/libraries/hyperlane-sealevel-connection-client/Cargo.toml
```diff
@@ -18,3 +18,6 @@ hyperlane-sealevel-igp = { path = "../../programs/hyperlane-sealevel-igp", featu
 
 [lib]
 crate-type = ["cdylib", "lib"]
+
+[profile.release]
+overflow-checks = true
```

### rust/sealevel/libraries/hyperlane-sealevel-token/Cargo.toml
```diff
@@ -29,3 +29,6 @@ serializable-account-meta = { path = "../serializable-account-meta" }
 
 [lib]
 crate-type = ["cdylib", "lib"]
+
+[profile.release]
+overflow-checks = true
```

### rust/sealevel/libraries/interchain-security-module-interface/Cargo.toml
```diff
@@ -12,3 +12,6 @@ spl-type-length-value.workspace = true
 
 [lib]
 crate-type = ["cdylib", "lib"]
+
+[profile.release]
+overflow-checks = true
```

### rust/sealevel/libraries/message-recipient-interface/Cargo.toml
```diff
@@ -14,3 +14,6 @@ hyperlane-core = { path = "../../../hyperlane-core" }
 
 [lib]
 crate-type = ["cdylib", "lib"]
+
+[profile.release]
+overflow-checks = true
```

### rust/sealevel/libraries/multisig-ism/Cargo.toml
```diff
@@ -23,3 +23,6 @@ hex.workspace = true
 
 [lib]
 crate-type = ["cdylib", "lib"]
+
+[profile.release]
+overflow-checks = true
```

### rust/sealevel/libraries/serializable-account-meta/Cargo.toml
```diff
@@ -11,3 +11,6 @@ solana-program.workspace = true
 
 [lib]
 crate-type = ["cdylib", "lib"]
+
+[profile.release]
+overflow-checks = true
```

### rust/sealevel/libraries/test-transaction-utils/Cargo.toml
```diff
@@ -12,3 +12,6 @@ solana-sdk.workspace = true
 
 [lib]
 crate-type = ["cdylib", "lib"]
+
+[profile.release]
+overflow-checks = true
```

### rust/sealevel/libraries/test-utils/Cargo.toml
```diff
@@ -24,3 +24,6 @@ serializable-account-meta = { path = "../serializable-account-meta" }
 
 [lib]
 crate-type = ["cdylib", "lib"]
+
+[profile.release]
+overflow-checks = true
```

### rust/sealevel/programs/hyperlane-sealevel-igp-test/Cargo.toml
```diff
@@ -17,3 +17,6 @@ hyperlane-sealevel-igp = { path = "../hyperlane-sealevel-igp" }
 solana-program-test.workspace = true
 solana-sdk.workspace = true
 hyperlane-test-utils = { path = "../../libraries/test-utils" }
+
+[profile.release]
+overflow-checks = true
```
