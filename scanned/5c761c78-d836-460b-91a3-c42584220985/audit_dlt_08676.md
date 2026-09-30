# [?] Merge branch 'tomas/fix-verify-sig-panic' (#3543)

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2024-07-24
Source: https://github.com/namada-net/namada/commit/f20ac6c9280584a345c56461fdd853725bc1aed0
Type: security-commit

## Details
Merge branch 'tomas/fix-verify-sig-panic' (#3543)

* origin/tomas/fix-verify-sig-panic:
  changelog: add #3543
  tx: fix possible panic in sig verification

## Patch
### .changelog/unreleased/bug-fixes/3543-fix-verify-sig-panic.md
```diff
@@ -0,0 +1,2 @@
+- Fixed a possible panic in transaction signatures verification missing expected
+  signature(s). ([\#3543](https://github.com/anoma/namada/pull/3543))
\ No newline at end of file
```

### crates/tx/src/types.rs
```diff
@@ -48,6 +48,8 @@ pub enum VerifySigError {
     InvalidSectionSignature(String),
     #[error("The number of PKs overflows u8::MAX")]
     PksOverflow,
+    #[error("An expected signature is missing.")]
+    MissingSignature,
 }
 
 #[allow(missing_docs)]
@@ -558,18 +560,19 @@ impl Authorization {
             // Verify the signatures against the subset of this section's public
             // keys that are also in the given map
             Signer::PubKeys(pks) => {
+                let hash = self.get_raw_hash();
                 for (idx, pk) in pks.iter().enumerate() {
                     if let Some(map_idx) =
                         public_keys_index_map.get_index_from_public_key(pk)
                     {
                         let sig_idx = u8::try_from(idx)
                             .map_err(|_| VerifySigError::PksOverflow)?;
                         consume_verify_sig_gas()?;
-                        common::SigScheme::verify_signature(
-                            pk,
-                            &self.get_raw_hash(),
-                            &self.signatures[&sig_idx],
-                        )?;
+                        let sig = self
+                            .signatures
+                            .get(&sig_idx)
+                            .ok_or(VerifySigError::MissingSignature)?;
+                        common::SigScheme::verify_signature(pk, &hash, sig)?;
                         verified_pks.insert(map_idx);
                         // Cannot overflow
                         #[allow(clippy::arithmetic_side_effects)]
```
