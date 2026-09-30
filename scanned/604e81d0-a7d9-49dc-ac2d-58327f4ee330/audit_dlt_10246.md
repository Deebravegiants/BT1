# [?] CVE-2022-24713 fix

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2022-03-09
Source: https://github.com/Phala-Network/phala-blockchain/commit/7cff4d40a5f3a70fe788256e8a944f7832f108af
Type: security-commit

## Details
CVE-2022-24713 fix

## Patch
### diem/types/Cargo.toml
```diff
@@ -35,7 +35,7 @@ aes-gcm = { path = "../vendor/aes-gcm", version = "0.8.0" }
 move-core-types = { path = "../language/move-core/types", version = "0.1.0" }
 
 [dev-dependencies]
-regex = "1.4.3"
+regex = "1.5.5"
 proptest = "0.10.1"
 proptest-derive = "0.2.0"
 serde_json = { git = "https://github.com/mesalock-linux/serde-json-sgx.git" }
```
