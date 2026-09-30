# [?] keymanager/src/churp: Fix overflow in test

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2024-03-11
Source: https://github.com/oasisprotocol/oasis-core/commit/cf1d3371bb1f60b5f8a9cfc417867f8f8fb782b6
Type: security-commit

## Details
keymanager/src/churp: Fix overflow in test

## Patch
### keymanager/src/churp/storage.rs
```diff
@@ -191,7 +191,7 @@ mod tests {
             .insert(wrong_key, encrypted_polynomial.clone())
             .expect("bivariate polynomial should be stored");
 
-        encrypted_polynomial[0] += 1;
+        encrypted_polynomial[0] = encrypted_polynomial[0].saturating_add(1);
         untrusted
             .insert(right_key, encrypted_polynomial.clone())
             .expect("bivariate polynomial should be stored");
@@ -231,7 +231,7 @@ mod tests {
 
         // Corrupted ciphertext, decryption should fail.
         let mut ciphertext = Storage::encrypt_bivariate_polynomial(&polynomial, churp_id, round);
-        ciphertext[0] += 1;
+        ciphertext[0] = ciphertext[0].saturating_add(1);
         Storage::decrypt_bivariate_polynomial::<p384::Scalar>(&mut ciphertext, churp_id, round)
             .expect_err("decryption of bivariate polynomial should fail");
     }
```
