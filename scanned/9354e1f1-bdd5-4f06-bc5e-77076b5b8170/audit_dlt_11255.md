# [?] fix: avoid panic on invalid inputs for ecdsa verification (#11160)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-01-27
Source: https://github.com/noir-lang/noir/commit/a74b9974e578c2bf6690a7a7f215b3755d500abe
Type: security-commit

## Details
fix: avoid panic on invalid inputs for ecdsa verification (#11160)

Co-authored-by: Tom French <15848336+TomAFrench@users.noreply.github.com>

## Patch
### acvm-repo/blackbox_solver/src/ecdsa/secp256k1.rs
```diff
@@ -1,12 +1,12 @@
 use acir::BlackBoxFunc;
-use k256::elliptic_curve::sec1::FromEncodedPoint;
-use k256::{FieldBytes, elliptic_curve::PrimeField};
 
 use k256::{
     AffinePoint, EncodedPoint, ProjectivePoint, PublicKey,
     elliptic_curve::{
+        PrimeField,
+        ops::Reduce,
         scalar::IsHigh,
-        sec1::{Coordinates, ToEncodedPoint},
+        sec1::{Coordinates, FromEncodedPoint, ToEncodedPoint},
     },
 };
 use k256::{Scalar, ecdsa::Signature};
@@ -67,12 +67,10 @@ pub(super) fn verify_signature(
     }
     let pubkey = pubkey.unwrap();
 
-    // Note: This will panic if `hashed_msg >= k256::Secp256k1::ORDER`.
-    // In this scenario we should just take the leftmost bits from `hashed_msg` up to the group order length.
-    let z = Scalar::from_repr(
-        FieldBytes::try_from_iter(hashed_msg.iter().copied()).expect("slice length mismatch"),
-    )
-    .unwrap();
+    // Convert the hashed message to a scalar.
+    // Per ECDSA specification (SEC 1, section 4.1.4), if `hashed_msg >= k256::Secp256k1::ORDER`,
+    // the message hash should be reduced modulo the curve order.
+    let z = <Scalar as Reduce<k256::U256>>::reduce(&k256::U256::from_be_slice(hashed_msg));
 
     // Finished converting bytes into data structures
 
@@ -96,10 +94,27 @@ pub(super) fn verify_signature(
         + (ProjectivePoint::from(*pubkey.as_affine()) * u2))
         .to_affine();
 
+    // Compare R.x with signature's r component.
     match R.to_encoded_point(false).coordinates() {
-        Coordinates::Uncompressed { x, y: _ } => Ok(Scalar::from_repr(*x).unwrap().eq(&r)),
+        Coordinates::Uncompressed { x, y: _ } => {
+            // The conversion from R.x to a scalar can fail if R.x >= curve_order (a possible but rare case).
+            // In this case, the signature is invalid per ECDSA specification, so we return false.
+            // The prover will handle this gracefully - it should generate a proof that fails verification.
+            Ok(Scalar::from_repr(*x).into_option().map_or_else(
+                || {
+                    log::warn!(
+                        "ECDSA Secp256k1 verification: R.x coordinate exceeds scalar field order - signature is invalid"
+                    );
+                    false
+                },
+                |scalar| scalar == *r,
+            ))
+        }
         Coordinates::Identity => Ok(false),
-        _ => unreachable!("Point is uncompressed"),
+        _ => Err(BlackBoxResolutionError::Failed(
+            BlackBoxFunc::EcdsaSecp256k1,
+            "Unexpected coordinate encoding".to_string(),
+        )),
     }
 }
 
```

### acvm-repo/blackbox_solver/src/ecdsa/secp256r1.rs
```diff
@@ -1,13 +1,12 @@
 use acir::BlackBoxFunc;
-use p256::elliptic_curve::PrimeField;
-use p256::elliptic_curve::sec1::FromEncodedPoint;
 
-use p256::FieldBytes;
 use p256::{
     AffinePoint, EncodedPoint, ProjectivePoint, PublicKey,
     elliptic_curve::{
+        PrimeField,
+        ops::Reduce,
         scalar::IsHigh,
-        sec1::{Coordinates, ToEncodedPoint},
+        sec1::{Coordinates, FromEncodedPoint, ToEncodedPoint},
     },
 };
 use p256::{Scalar, ecdsa::Signature};
@@ -68,12 +67,10 @@ pub(super) fn verify_signature(
     };
     let pubkey = pubkey.unwrap();
 
-    // Note: This will panic if `hashed_msg >= p256::NistP256::ORDER`.
-    // In this scenario we should just take the leftmost bits from `hashed_msg` up to the group order length.
-    let z = Scalar::from_repr(
-        FieldBytes::try_from_iter(hashed_msg.iter().copied()).expect("slice length mismatch"),
-    )
-    .unwrap();
+    // Convert the hashed message to a scalar.
+    // Per ECDSA specification (SEC 1, section 4.1.4), if `hashed_msg >= p256::NistP256::ORDER`,
+    // the message hash should be reduced modulo the curve order.
+    let z = <Scalar as Reduce<p256::U256>>::reduce(&p256::U256::from_be_slice(hashed_msg));
 
     // Finished converting bytes into data structures
 
@@ -98,9 +95,23 @@ pub(super) fn verify_signature(
         .to_affine();
 
     match R.to_encoded_point(false).coordinates() {
-        Coordinates::Uncompressed { x, y: _ } => Ok(Scalar::from_repr(*x).unwrap().eq(&r)),
+        Coordinates::Uncompressed { x, y: _ } => {
+            // The conversion from R.x to a scalar can fail if R.x >= curve_order (a possible but rare case).
+            // In this case, the signature is invalid per ECDSA specification, so we return false.
+            // The prover will handle this gracefully - it should generate a proof that fails verification.
+            Ok(Scalar::from_repr(*x).into_option().map_or_else(
+                || {
+                    log::warn!("Failed to convert R.x coordinate to scalar for ECDSA verification");
+                    false
+                },
+                |scalar| scalar == *r,
+            ))
+        }
         Coordinates::Identity => Ok(false),
-        _ => unreachable!("Point is uncompressed"),
+        _ => Err(BlackBoxResolutionError::Failed(
+            BlackBoxFunc::EcdsaSecp256r1,
+            "Unexpected coordinate encoding".to_string(),
+        )),
     }
 }
 
```

### test_programs/execution_panic/ecdsa_secp256k1_msg_equals_order/Nargo.toml
```diff
@@ -1,7 +0,0 @@
-[package]
-name = "ecdsa_secp256k1_msg_equals_order"
-description = "ECDSA secp256k1 verification should fail when hashed_msg equals ORDER"
-type = "bin"
-authors = [""]
-
-[dependencies]
```

### test_programs/execution_panic/ecdsa_secp256k1_msg_equals_order/src/main.nr
```diff
@@ -1,5 +0,0 @@
-fn main(hashed_message: [u8; 32], pub_key_x: [u8; 32], pub_key_y: [u8; 32], signature: [u8; 64]) {
-    let valid_signature =
-        std::ecdsa_secp256k1::verify_signature(pub_key_x, pub_key_y, signature, hashed_message);
-    assert(valid_signature);
-}
```

### test_programs/execution_success/ecdsa_secp256k1_invalid_inputs/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "ecdsa_secp256k1_invalid_inputs"
+description = "ECDSA secp256k1 verification should return false when inputs are invalid"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/execution_success/ecdsa_secp256k1_invalid_inputs/Prover.toml
```diff
@@ -168,3 +168,36 @@ signature = [
     0xcd,
     0x55,
 ]
+
+hashed_message_2 = [
+    # hashed_msg = 1
+    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
+    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
+    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
+    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
+]
+
+pub_key_x_2 = [
+    0x23, 0xc9, 0x60, 0x0e, 0x95, 0x68, 0x57, 0x47,
+    0xe8, 0x9d, 0xcb, 0x90, 0x5b, 0xff, 0xf5, 0xa1,
+    0x5c, 0x77, 0xc0, 0x3a, 0x2e, 0x29, 0x73, 0x41,
+    0x6e, 0x36, 0xd4, 0x73, 0xe9, 0xce, 0x9f, 0x72,
+]
+pub_key_y_2 = [
+    0x6b, 0x55, 0x85, 0x03, 0xba, 0xda, 0xf0, 0x27,
+    0x6c, 0x4e, 0x01, 0xdc, 0x70, 0xe3, 0x0c, 0x13,
+    0x2b, 0x35, 0xe8, 0xc2, 0x25, 0x0d, 0xe8, 0xa3,
+    0xc0, 0xbd, 0x2a, 0xe4, 0x51, 0xe9, 0xb7, 0xda,
+]
+signature_2 =  [
+    # r = 1 (bytes 0..32, big-endian)
+    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
+    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
+    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
+    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
+    # s = 1 (bytes 32..64, big-endian)
+    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
+    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
+    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
+    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
+]
\ No newline at end of file
```

### test_programs/execution_success/ecdsa_secp256k1_invalid_inputs/src/main.nr
```diff
@@ -0,0 +1,27 @@
+fn main(
+    hashed_message: [u8; 32],
+    pub_key_x: [u8; 32],
+    pub_key_y: [u8; 32],
+    signature: [u8; 64],
+    hashed_message_2: [u8; 32],
+    pub_key_x_2: [u8; 32],
+    pub_key_y_2: [u8; 32],
+    signature_2: [u8; 64],
+) {
+    // First test: message equals the order of the curve
+    let valid_signature =
+        std::ecdsa_secp256k1::verify_signature(pub_key_x, pub_key_y, signature, hashed_message);
+    assert(!valid_signature);
+
+    // Second test: R.x >= curve order
+    // signature with r = s = 1 and message = 1
+    // Hence, in ecdsa verification, u1 and u2 are 1, so R = G (generator) + P (pubkey)
+    // P is chosen so that P = R - G, with R.x = curve's field modulus - 3
+    let valid_signature = std::ecdsa_secp256k1::verify_signature(
+        pub_key_x_2,
+        pub_key_y_2,
+        signature_2,
+        hashed_message_2,
+    );
+    assert(!valid_signature);
+}
```

### test_programs/execution_success/ecdsa_secp256r1_msg_equals_order/Nargo.toml
```diff
@@ -1,6 +1,6 @@
 [package]
 name = "ecdsa_secp256r1_msg_equals_order"
-description = "ECDSA secp256r1 verification should fail when hashed_msg equals ORDER"
+description = "ECDSA secp256r1 verification should return false when hashed_msg equals ORDER"
 type = "bin"
 authors = [""]
 
```

### test_programs/execution_success/ecdsa_secp256r1_msg_equals_order/src/main.nr
```diff
@@ -1,5 +1,5 @@
 fn main(hashed_message: [u8; 32], pub_key_x: [u8; 32], pub_key_y: [u8; 32], signature: [u8; 64]) {
     let valid_signature =
         std::ecdsa_secp256r1::verify_signature(pub_key_x, pub_key_y, signature, hashed_message);
-    assert(valid_signature);
+    assert(!valid_signature);
 }
```

### tooling/nargo_cli/tests/snapshots/execution_success/ecdsa_secp256k1_invalid_inputs/execute__tests__expanded.snap
```diff
@@ -0,0 +1,25 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: expanded_code
+---
+fn main(
+    hashed_message: [u8; 32],
+    pub_key_x: [u8; 32],
+    pub_key_y: [u8; 32],
+    signature: [u8; 64],
+    hashed_message_2: [u8; 32],
+    pub_key_x_2: [u8; 32],
+    pub_key_y_2: [u8; 32],
+    signature_2: [u8; 64],
+) {
+    let valid_signature: bool =
+        std::ecdsa_secp256k1::verify_signature(pub_key_x, pub_key_y, signature, hashed_message);
+    assert(!valid_signature);
+    let valid_signature: bool = std::ecdsa_secp256k1::verify_signature(
+        pub_key_x_2,
+        pub_key_y_2,
+        signature_2,
+        hashed_message_2,
+    );
+    assert(!valid_signature);
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/ecdsa_secp256k1_invalid_inputs/execute__tests__stdout.snap
```diff
@@ -0,0 +1,5 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stdout
+---
+
```
