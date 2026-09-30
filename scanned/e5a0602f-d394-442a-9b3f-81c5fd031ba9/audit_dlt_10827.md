# [?] Bump nomt to 1.0.3 with panic fix (#2191)

## Summary
Severity: Unknown
Chain: Sovereign SDK
Component: Sovereign-Labs/sovereign-sdk
Published: 2025-12-08
Source: https://github.com/Sovereign-Labs/sovereign-sdk/commit/548c4f47d068ce21af710914f3cbd27d250a7357
Type: security-commit

## Details
Bump nomt to 1.0.3 with panic fix (#2191)

## Patch
### Cargo.lock
```diff
@@ -7093,9 +7093,9 @@ dependencies = [
 
 [[package]]
 name = "nomt"
-version = "1.0.2"
+version = "1.0.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "705307a2ab047b0ac978479652ba19e995d022794785b6a165a0f7f24739908c"
+checksum = "7cebfa5217b0c23f8088cdd2e9b8033db6ba49a968cfbf0a35433043b76b8f93"
 dependencies = [
  "ahash",
  "anyhow",
@@ -7123,9 +7123,9 @@ dependencies = [
 
 [[package]]
 name = "nomt-core"
-version = "1.0.2"
+version = "1.0.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "feeb4e411c8185c33c906539b78330a8478a2d4819de338efb6511b33cc73207"
+checksum = "e86909b9e6666306bb3878401e8fc8afe4bcd99771acf30d94ad0bab1c1173f9"
 dependencies = [
  "arrayvec",
  "bitvec",
```

### Cargo.toml
```diff
@@ -191,8 +191,8 @@ reltester = { git = "https://github.com/sovereign-labs/reltester.git", rev = "d6
 rockbound = { git = "https://github.com/sovereign-labs/rockbound", rev = "bb21a29cee84d4491850acd553b150ec6cc1ca71" }
 nmt-rs = { version = "0.2.5", features = ["serde", "borsh"] }
 # External dependencies
-nomt-core = { version = "1.0.2", default-features = false, features = ["borsh", "serde"] }
-nomt = { version = "1.0.2", default-features = false, features = ["borsh", "serde"] }
+nomt-core = { version = "1.0.3", default-features = false, features = ["borsh", "serde"] }
+nomt = { version = "1.0.3", default-features = false, features = ["borsh", "serde"] }
 
 anyhow = { version = "1.0.95" }
 async-trait = "0.1.81"
```

### examples/demo-rollup/provers/risc0/guest-celestia/Cargo.lock
```diff
@@ -2572,9 +2572,9 @@ checksum = "a5b0c77c1b780822bc749a33e39aeb2c07584ab93332303babeabb645298a76e"
 
 [[package]]
 name = "nomt-core"
-version = "1.0.2"
+version = "1.0.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "feeb4e411c8185c33c906539b78330a8478a2d4819de338efb6511b33cc73207"
+checksum = "e86909b9e6666306bb3878401e8fc8afe4bcd99771acf30d94ad0bab1c1173f9"
 dependencies = [
  "arrayvec",
  "bitvec",
```

### examples/demo-rollup/provers/risc0/guest-mock/Cargo.lock
```diff
@@ -2283,9 +2283,9 @@ checksum = "a5b0c77c1b780822bc749a33e39aeb2c07584ab93332303babeabb645298a76e"
 
 [[package]]
 name = "nomt-core"
-version = "1.0.2"
+version = "1.0.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "feeb4e411c8185c33c906539b78330a8478a2d4819de338efb6511b33cc73207"
+checksum = "e86909b9e6666306bb3878401e8fc8afe4bcd99771acf30d94ad0bab1c1173f9"
 dependencies = [
  "arrayvec",
  "bitvec",
```

### examples/demo-rollup/provers/sp1/guest-celestia/Cargo.lock
```diff
@@ -3488,9 +3488,9 @@ dependencies = [
 
 [[package]]
 name = "nomt-core"
-version = "1.0.2"
+version = "1.0.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "feeb4e411c8185c33c906539b78330a8478a2d4819de338efb6511b33cc73207"
+checksum = "e86909b9e6666306bb3878401e8fc8afe4bcd99771acf30d94ad0bab1c1173f9"
 dependencies = [
  "arrayvec",
  "bitvec",
```

### examples/demo-rollup/provers/sp1/guest-mock/Cargo.lock
```diff
@@ -3204,9 +3204,9 @@ dependencies = [
 
 [[package]]
 name = "nomt-core"
-version = "1.0.2"
+version = "1.0.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "feeb4e411c8185c33c906539b78330a8478a2d4819de338efb6511b33cc73207"
+checksum = "e86909b9e6666306bb3878401e8fc8afe4bcd99771acf30d94ad0bab1c1173f9"
 dependencies = [
  "arrayvec",
  "bitvec",
```
