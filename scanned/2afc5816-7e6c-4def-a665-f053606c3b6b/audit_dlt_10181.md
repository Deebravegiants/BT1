# [?] Merge pull request #5593 from oasisprotocol/peternose/trivial/fix-overflow

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2024-03-11
Source: https://github.com/oasisprotocol/oasis-core/commit/4f7767c4a5c24250ef0147038afebadd124914e1
Type: security-commit

## Details
Merge pull request #5593 from oasisprotocol/peternose/trivial/fix-overflow

keymanager/src/churp: Fix overflow in test

## Patch
### keymanager/src/churp/storage.rs
```diff
@@ -142,7 +142,7 @@ impl Storage {
 mod tests {
     use std::sync::Arc;
 
-    use rand::rngs::OsRng;
+    use rand::{rngs::StdRng, SeedableRng};
 
     use oasis_core_runtime::storage::{KeyValue, UntrustedInMemoryStorage};
 
@@ -152,9 +152,10 @@ mod tests {
 
     #[test]
     fn test_store_load_polynomial() {
+        let mut rng: StdRng = SeedableRng::from_seed([1u8; 32]);
         let untrusted = Arc::new(UntrustedInMemoryStorage::new());
         let storage = Storage::new(untrusted.clone());
-        let polynomial = BivariatePolynomial::<p384::Scalar>::random(2, 4, &mut OsRng);
+        let polynomial = BivariatePolynomial::<p384::Scalar>::random(2, 4, &mut rng);
         let churp_id = 1;
         let round = 10;
 
@@ -190,7 +191,7 @@ mod tests {
             .insert(wrong_key, encrypted_polynomial.clone())
             .expect("bivariate polynomial should be stored");
 
-        encrypted_polynomial[0] += 1;
+        encrypted_polynomial[0] = encrypted_polynomial[0].saturating_add(1);
         untrusted
             .insert(right_key, encrypted_polynomial.clone())
             .expect("bivariate polynomial should be stored");
@@ -208,7 +209,8 @@ mod tests {
 
     #[test]
     fn test_encrypt_decrypt_polynomial() {
-        let polynomial = BivariatePolynomial::<p384::Scalar>::random(2, 4, &mut OsRng);
+        let mut rng: StdRng = SeedableRng::from_seed([1u8; 32]);
+        let polynomial = BivariatePolynomial::<p384::Scalar>::random(2, 4, &mut rng);
         let churp_id = 1;
         let round = 10;
 
@@ -229,7 +231,7 @@ mod tests {
 
         // Corrupted ciphertext, decryption should fail.
         let mut ciphertext = Storage::encrypt_bivariate_polynomial(&polynomial, churp_id, round);
-        ciphertext[0] += 1;
+        ciphertext[0] = ciphertext[0].saturating_add(1);
         Storage::decrypt_bivariate_polynomial::<p384::Scalar>(&mut ciphertext, churp_id, round)
             .expect_err("decryption of bivariate polynomial should fail");
     }
```
