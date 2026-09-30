# [?] dcap: prevent crash if no advisoryIDs

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2024-02-05
Source: https://github.com/Phala-Network/phala-blockchain/commit/cdaa24ef4fc8bd0ab6a58d354dd3d7ca9a9728e5
Type: security-commit

## Details
dcap: prevent crash if no advisoryIDs

## Patch
### crates/sgx-attestation/src/dcap/tcb_info.rs
```diff
@@ -22,7 +22,7 @@ pub struct TcbLevel {
     pub tcb: Tcb,
     pub tcb_date: String,
     pub tcb_status: String,
-    #[serde(rename = "advisoryIDs")]
+    #[serde(rename = "advisoryIDs", default)]
     pub advisory_ids: Vec<String>,
 }
 
```
