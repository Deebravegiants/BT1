# [?] fix: panic when sending funds to invalid address (#3457)

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2023-12-05
Source: https://github.com/penumbra-zone/penumbra/commit/ab12795f58ea69b21736ebd593f45152416f1cea
Type: security-commit

## Details
fix: panic when sending funds to invalid address (#3457)

* crypto: add method to infallibly expand `ClueKey`

* fix: expand clue key infallibly when creating clues (closes #3332)

* test: invalid clue keys should expand infallibly

## Patch
### crates/core/transaction/src/plan/clue.rs
```diff
@@ -1,4 +1,4 @@
-use decaf377_fmd::{Clue, ExpandedClueKey};
+use decaf377_fmd::Clue;
 use penumbra_keys::Address;
 use penumbra_proto::{core::transaction::v1alpha1 as pb, DomainType};
 
@@ -30,7 +30,7 @@ impl CluePlan {
     /// Create a [`Clue`] from the [`CluePlan`].
     pub fn clue(&self) -> Clue {
         let clue_key = self.address.clue_key();
-        let expanded_clue_key = ExpandedClueKey::new(clue_key).expect("valid address");
+        let expanded_clue_key = clue_key.expand_infallible();
         expanded_clue_key
             .create_clue_deterministic(self.precision_bits, self.rseed)
             .expect("can construct clue key")
```

### crates/crypto/decaf377-fmd/src/clue_key.rs
```diff
@@ -2,7 +2,7 @@ use std::{cell::RefCell, convert::TryFrom};
 
 use ark_ff::{Field, PrimeField};
 use bitvec::{array::BitArray, order};
-use decaf377::{FieldExt, Fr};
+use decaf377::{FieldExt, Fq, Fr};
 use rand_core::{CryptoRng, RngCore};
 
 use crate::{hash, hkd, Clue, Error, MAX_PRECISION};
@@ -34,6 +34,22 @@ impl ClueKey {
     pub fn expand(&self) -> Result<ExpandedClueKey, Error> {
         ExpandedClueKey::new(self)
     }
+
+    /// Expand this clue key encoding.
+    ///
+    /// This method always results in a valid clue key, though the clue key may not have
+    /// a known detection key.
+    pub fn expand_infallible(&self) -> ExpandedClueKey {
+        let mut counter = 0u32;
+        loop {
+            counter += 1;
+            let ck_fq_incremented = Fq::from_le_bytes_mod_order(&self.0) + Fq::from(counter);
+            let ck = ClueKey(ck_fq_incremented.to_bytes());
+            if let Ok(eck) = ck.expand() {
+                return eck;
+            }
+        }
+    }
 }
 
 impl ExpandedClueKey {
@@ -177,3 +193,16 @@ impl TryFrom<&[u8]> for ClueKey {
         }
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+
+    #[test]
+    fn test_clue_key_infallible_expand() {
+        let valid_ck = ClueKey(decaf377::basepoint().vartime_compress().0);
+        let ck_fq_invalid = Fq::from_le_bytes_mod_order(&valid_ck.0) + Fq::from(1u64);
+        let invalid_ck = ClueKey(ck_fq_invalid.to_bytes());
+        let _eck = invalid_ck.expand_infallible();
+    }
+}
```
