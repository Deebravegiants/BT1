# [?] Fix base64 panic in from_base64

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2026-06-16
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/339682002d1ab01463f46bb2a6ed3f1ec5a1a17a
Type: security-commit

## Details
Fix base64 panic in from_base64

In sign_message, the from_base64 function can panic if the string has
both a length of 88 bytes, and decodes to an array of bytes > 65. This
can happen for a string of 88 "A" characters, for example. Further, the
function incorrectly parses base64 strings that produce 64 byte arrays.
While the latter is likely caught by the underlying secp parsing, both
should be checked to provide a more meaningful error return.

Add checks for non-65 byte base64 decoding in from_base64, returning
an InvalidLength error for 64 or 66 byte decodes. Also prevent panic on
66 byte decode.

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
```
