# [?] Prevent crash if no advisoryURL or advisoryIDs

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2023-12-06
Source: https://github.com/Phala-Network/phala-blockchain/commit/03442db8e6ab4d32dfbcec152d8a18af136662c5
Type: security-commit

## Details
Prevent crash if no advisoryURL or advisoryIDs

## Patch
### crates/sgx-attestation/src/ias.rs
```diff
@@ -43,9 +43,9 @@ pub struct RaReport {
     pub timestamp: String,
     pub version: u8,
     pub epid_pseudonym: String,
-    #[serde(rename = "advisoryURL")]
+    #[serde(rename = "advisoryURL", default)]
     pub advisory_url: String,
-    #[serde(rename = "advisoryIDs")]
+    #[serde(rename = "advisoryIDs", default)]
     pub advisory_ids: Vec<String>,
     pub isv_enclave_quote_status: String,
     pub isv_enclave_quote_body: String,
```
