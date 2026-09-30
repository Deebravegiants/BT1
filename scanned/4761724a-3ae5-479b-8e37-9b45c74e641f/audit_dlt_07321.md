# [?] chore(crypto): CRP-2038 Remove workaround for RSA signature malleability (#5080)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2025-05-16
Source: https://github.com/dfinity/ic/commit/917b62727246488923bca61a2048cf628ad892a7
Type: security-commit

## Details
chore(crypto): CRP-2038 Remove workaround for RSA signature malleability (#5080)

An old version of the `rsa` crate had issues with signature
malleability, where it would accept signatures that were zero-padded to
be longer than the modulus, as well as signatures which were greater
than the public modulus.

These were fixed in a later version of the `rsa` crate, which we have
already upgraded to. But the workaround to check for the malformed
signatures was not removed at that time.

## Patch
### rs/crypto/internal/crypto_lib/basic_sig/rsa_pkcs1/src/lib.rs
```diff
@@ -160,37 +160,6 @@ impl RsaPublicKey {
     /// (https://datatracker.ietf.org/doc/html/rfc8017#section-8.2) and used by
     /// the IC for webauthn (https://docs.dfinity.systems/spec/public/#webauthn)
     pub fn verify_pkcs1_sha256(&self, message: &[u8], signature: &[u8]) -> CryptoResult<()> {
-        // The version of rsa crate that we use has a signature malleability bug
-        // https://github.com/RustCrypto/RSA/issues/272 which does not seem
-        // directly to be any real problem, but worth avoiding.
-        //
-        // There is an updated version of the crate but upgrading
-        // requires significant changes, see CRP-2038
-        let modulus_bytes = self.key.n().bits().div_ceil(8); // rounding up
-
-        if signature.len() > modulus_bytes {
-            return Err(CryptoError::SignatureVerification {
-                algorithm: AlgorithmId::RsaSha256,
-                public_key_bytes: self.as_der().to_vec(),
-                sig_bytes: signature.to_vec(),
-                internal_error: format!(
-                    "Signature is {} bytes but public modulus only {}",
-                    signature.len(),
-                    modulus_bytes
-                ),
-            });
-        }
-        let sig = rsa::BigUint::from_bytes_be(signature);
-
-        if &sig > self.key.n() {
-            return Err(CryptoError::SignatureVerification {
-                algorithm: AlgorithmId::RsaSha256,
-                public_key_bytes: self.as_der().to_vec(),
-                sig_bytes: signature.to_vec(),
-                internal_error: "Signature is larger than public modulus".to_string(),
-            });
-        }
-
         let digest = Sha256::hash(message);
 
         match &self
```
