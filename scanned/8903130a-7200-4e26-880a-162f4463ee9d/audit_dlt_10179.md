# [?] secret-sharing/src/churp: Fix threshold overflow

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2024-05-11
Source: https://github.com/oasisprotocol/oasis-core/commit/ddf51345a9a468dd6ec72b5292df9c8904cd81c9
Type: security-commit

## Details
secret-sharing/src/churp: Fix threshold overflow

## Patch
### keymanager/src/churp/handler.rs
```diff
@@ -1038,7 +1038,7 @@ impl Churp {
                 // will detect the polynomial change because the checksum
                 // of the verification matrix in the submitted application
                 // will also change.
-                let dealer = Dealer::new(threshold, dealing_phase, &mut OsRng);
+                let dealer = Dealer::new(threshold, dealing_phase, &mut OsRng)?;
 
                 // Encrypt and store the polynomial in case of a restart.
                 let polynomial = dealer.bivariate_polynomial();
```

### secret-sharing/src/churp/dealer.rs
```diff
@@ -1,7 +1,6 @@
 //! CHURP dealer.
 
 use anyhow::Result;
-
 use rand_core::RngCore;
 
 use crate::{
@@ -12,7 +11,7 @@ use crate::{
     },
 };
 
-use super::{HandoffKind, ShareholderId};
+use super::{Error, HandoffKind, ShareholderId};
 
 /// Dealer is responsible for generating a secret bivariate polynomial,
 /// computing a verification matrix, and deriving secret shares for other
@@ -35,14 +34,16 @@ where
     S: Suite,
 {
     /// Creates a new dealer.
-    pub fn new(threshold: u8, dealing_phase: bool, rng: &mut impl RngCore) -> Self {
+    pub fn new(threshold: u8, dealing_phase: bool, rng: &mut impl RngCore) -> Result<Self> {
         let dx = threshold;
-        let dy = 2 * threshold;
+        let dy = threshold.checked_mul(2).ok_or(Error::ThresholdTooLarge)?;
 
-        match dealing_phase {
+        let dealer = match dealing_phase {
             true => Dealer::random(dx, dy, rng),
             false => Dealer::zero_hole(dx, dy, rng),
-        }
+        };
+
+        Ok(dealer)
     }
 
     /// Creates a new dealer with a random bivariate polynomial.
@@ -113,7 +114,7 @@ mod tests {
 
         let threshold = 2;
         for dealing_phase in vec![true, false] {
-            let dealer = Dealer::new(threshold, dealing_phase, &mut rng);
+            let dealer = Dealer::new(threshold, dealing_phase, &mut rng).unwrap();
             assert_eq!(dealer.verification_matrix().is_zero_hole(), !dealing_phase);
             assert_eq!(dealer.bivariate_polynomial().deg_x, 2);
             assert_eq!(dealer.bivariate_polynomial().deg_y, 4);
@@ -123,7 +124,7 @@ mod tests {
 
         let threshold = 0;
         for dealing_phase in vec![true, false] {
-            let dealer = Dealer::new(threshold, dealing_phase, &mut rng);
+            let dealer = Dealer::new(threshold, dealing_phase, &mut rng).unwrap();
             assert_eq!(dealer.verification_matrix().is_zero_hole(), !dealing_phase);
             assert_eq!(dealer.bivariate_polynomial().deg_x, 0);
             assert_eq!(dealer.bivariate_polynomial().deg_y, 0);
```

### secret-sharing/src/churp/errors.rs
```diff
@@ -22,6 +22,8 @@ pub enum Error {
     PolynomialDegreeMismatch,
     #[error("shareholder encoding failed")]
     ShareholderEncodingFailed,
+    #[error("threshold too large")]
+    ThresholdTooLarge,
     #[error("too many switch points")]
     TooManySwitchPoints,
     #[error("unknown shareholder")]
```

### secret-sharing/src/churp/handoff.rs
```diff
@@ -383,7 +383,7 @@ mod tests {
     ) -> HashMap<ShareholderId, Dealer> {
         let mut dealers = HashMap::new();
         for sh in committee.iter() {
-            let d = Dealer::new(threshold, dealing_phase, rng);
+            let d = Dealer::new(threshold, dealing_phase, rng).unwrap();
             dealers.insert(sh.clone(), d);
         }
         dealers
```
