# [?] Fix a possible panic in Bytes deserialization with Unicode.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2022-09-13
Source: https://github.com/Conflux-Chain/conflux-rust/commit/c72fa8b06ef8212ebd0fd2450bd132da4a9d55f0
Type: security-commit

## Details
Fix a possible panic in Bytes deserialization with Unicode.

## Patch
### client/src/rpc/types/bytes.rs
```diff
@@ -76,8 +76,10 @@ impl<'a> Visitor<'a> for BytesVisitor {
 
     fn visit_str<E>(self, value: &str) -> Result<Self::Value, E>
     where E: Error {
-        if value.len() >= 2 && &value[0..2] == "0x" && value.len() & 1 == 0 {
-            Ok(Bytes::new(FromHex::from_hex(&value[2..]).map_err(|e| {
+        if let (Some(s), true) =
+            (value.strip_prefix("0x"), value.len() & 1 == 0)
+        {
+            Ok(Bytes::new(FromHex::from_hex(s).map_err(|e| {
                 Error::custom(format!("Invalid hex: {}", e))
             })?))
         } else {
```
