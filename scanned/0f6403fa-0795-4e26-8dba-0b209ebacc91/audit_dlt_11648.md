# [?] Merge rust-bitcoin/rust-bitcoin#6381: Fix panic in `sign_message::MessageSignature::from_base64`

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2026-06-27
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/f7afcb38f2911cb8c26101d162960fb91e9f7c6d
Type: security-commit

## Details
Merge rust-bitcoin/rust-bitcoin#6381: Fix panic in `sign_message::MessageSignature::from_base64`

188f9f3080c5b117f78af1f1e467bc4f3178b1b2 Add regression test for from_base64 bug (Mitchell Bagot)
339682002d1ab01463f46bb2a6ed3f1ec5a1a17a Fix base64 panic in from_base64 (Mitchell Bagot)

Pull request description:

  In sign_message, the from_base64 function can panic if the string has both a length of 88 bytes, and decodes to an array of bytes > 65. This can happen for a string of 88 "A" characters, for example. Since decode_slice in base64 is functionally equivalent to
  decode_slice_unchecked (aside from an explicit panic) and correctness is significantly more important than performance for the soft deprecated sign_message module, this can be trivially fixed by replacing use of decode_slice_unchecked with decode_slice.
  
  - Patch 1 replaces the use of decode_slice_unchecked with decode_slice in from_base64 to prevent panic on insufficient slice length.
  - Patch 2 introduces a regression test for the logic, as provided by Project Loupe in #6376 
  
  Closes #6376


ACKs for top commit:
  apoelstra:
    ACK 188f9f3080c5b117f78af1f1e467bc4f3178b1b2; successfully ran local tests


Tree-SHA512: 0952cfcffc5703e40876748ead872605583348d57b1f9237670facb5e5c72d2c35ef3c1c4464acf11a25a5172d47ec57b2026af1afb1cbdd637f97eb16a055fd

## Patch
### bitcoin/src/sign_message.rs
```diff
@@ -132,11 +132,17 @@ mod message_signing {
                 if s.len() != 88 {
                     return Err(MessageSignatureError::InvalidLength);
                 }
-                let mut byte_array = [0; 65];
-                BASE64_STANDARD
+                let mut byte_array = [0; 66];
+                let decode_len = BASE64_STANDARD
                     .decode_slice_unchecked(s, &mut byte_array)
                     .map_err(|_| MessageSignatureError::InvalidBase64)?;
-                Self::from_byte_array(&byte_array).map_err(MessageSignatureError::from)
+                if decode_len != 65 {
+                    return Err(MessageSignatureError::InvalidLength);
+                }
+                let exact_bytes = byte_array[..65]
+                    .try_into()
+                    .expect("exactly 65 bytes exist in byte_array slice");
+                Self::from_byte_array(&exact_bytes).map_err(MessageSignatureError::from)
             }
 
             /// Converts to base64 encoding.
@@ -233,6 +239,9 @@ pub mod error {
 
 #[cfg(test)]
 mod tests {
+    #[cfg(feature = "base64")]
+    #[cfg(feature = "secp-recovery")]
+    use alloc::string::String;
     use alloc::string::ToString;
 
     use super::*;
@@ -318,4 +327,24 @@ mod tests {
         let p2pkh = Address::p2pkh(pubkey, NetworkKind::Main);
         assert_eq!(signature.is_signed_by_address(&p2pkh, msg_hash), Ok(false));
     }
+
+    #[test]
+    #[cfg(feature = "base64")]
+    #[cfg(feature = "secp-recovery")]
+    fn from_base64_rejects_non_65_byte_decode() {
+        // 88-char base64 can decode to 64, 65, or 66 bytes.
+        let input: String = "A".repeat(88);
+        let result = super::MessageSignature::from_base64(&input);
+        assert!(result.is_err());
+
+        let mut input: String = "A".repeat(86);
+        input.extend(['=', '=']);
+        let result = super::MessageSignature::from_base64(&input);
+        assert!(result.is_err());
+
+        let mut input: String = "A".repeat(87);
+        input.extend(['=']);
+        let result = super::MessageSignature::from_base64(&input);
+        assert!(result.is_err());
+    }
 }
```
