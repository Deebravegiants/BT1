# [?] CVE-2022-24713 fix

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2022-03-09
Source: https://github.com/Phala-Network/phala-blockchain/commit/64346ef1c2e00673ad88efbde96424aa62da20ed
Type: security-commit

## Details
CVE-2022-24713 fix

## Patch
### diem/language/move-core/types/Cargo.toml
```diff
@@ -33,7 +33,7 @@ short-hex-str = { path = "../../../common/short-hex-str", version = "0.1.0" }
 once_cell = { git = "https://github.com/mesalock-linux/once_cell-sgx.git" }
 proptest = "0.10.1"
 proptest-derive = "0.2.0"
-regex = "1.4.3"
+regex = "1.5.5"
 serde_json = "1.0.61"
 
 [features]
```
