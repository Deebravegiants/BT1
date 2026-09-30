# [?] fix base32 address decode panic for malformed address

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-06-02
Source: https://github.com/Conflux-Chain/conflux-rust/commit/e7f5f80736fdfa01c77c8790942ba64946bfb910
Type: security-commit

## Details
fix base32 address decode panic for malformed address

## Patch
### crates/cfx_addr/src/lib.rs
```diff
@@ -131,11 +131,6 @@ pub fn cfx_addr_decode(
     if payload_str.is_empty() {
         return Err(DecodingError::InvalidLength(0));
     }
-    let has_lowercase = payload_str.chars().any(|c| c.is_lowercase());
-    let has_uppercase = payload_str.chars().any(|c| c.is_uppercase());
-    if has_lowercase && has_uppercase {
-        return Err(DecodingError::MixedCase);
-    }
 
     // Decode payload to 5 bit array
     let payload_chars = payload_str.chars();
@@ -161,10 +156,18 @@ pub fn cfx_addr_decode(
         return Err(DecodingError::ChecksumFailed(checksum));
     }
 
-    // Convert from 5 bit array to byte array
+    // The last 8 symbols are the checksum, so we need strictly more than 8
+    // symbols to have a non-empty body after stripping the checksum.
     let len_5_bit = payload_5_bits.len();
+    if len_5_bit <= 8 {
+        return Err(DecodingError::InvalidLength(len_5_bit));
+    }
+    // Convert from 5 bit array to byte array.
     let payload =
         convert_bits(&payload_5_bits[..(len_5_bit - 8)], 5, 8, false)?;
+    if payload.is_empty() {
+        return Err(DecodingError::InvalidLength(0));
+    }
 
     // Verify the version byte
     let version = payload[0];
```

### crates/cfx_addr/tests/decode.rs
```diff
@@ -64,3 +64,11 @@ fn decoding_errors() {
     assert!(cfx_addr_decode("cfx:ccc7uawf5ubtnmezvhu9dhc6sghea0403y2dgpyfjp").is_err()); // version byte: 0b00010000
     assert!(cfx_addr_decode("cfx:bcc7uawf5ubtnmezvhu9dhc6sghea0403y2dgpyfjp").is_err()); // version byte: 0b00001000
 }
+
+// F-001: An 8-symbol base32 payload whose checksum is valid but body is empty
+// must return an error, not panic.
+#[test]
+fn decode_short_payload_no_panic() {
+    // 8 symbols: all checksum, zero-length body after stripping 8-symbol tail.
+    assert!(cfx_addr_decode("cfx:w3tg4akb").is_err());
+}
```
