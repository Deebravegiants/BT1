# [?] fix: do not crash when R is zero (#11122)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-01-08
Source: https://github.com/noir-lang/noir/commit/4a39a9a4dd53cb0e638cbf846fc34fb23c9b953d
Type: security-commit

## Details
fix: do not crash when R is zero (#11122)

## Patch
### acvm-repo/blackbox_solver/src/ecdsa/secp256k1.rs
```diff
@@ -98,6 +98,7 @@ pub(super) fn verify_signature(
 
     match R.to_encoded_point(false).coordinates() {
         Coordinates::Uncompressed { x, y: _ } => Ok(Scalar::from_repr(*x).unwrap().eq(&r)),
+        Coordinates::Identity => Ok(false),
         _ => unreachable!("Point is uncompressed"),
     }
 }
```

### acvm-repo/blackbox_solver/src/ecdsa/secp256r1.rs
```diff
@@ -99,6 +99,7 @@ pub(super) fn verify_signature(
 
     match R.to_encoded_point(false).coordinates() {
         Coordinates::Uncompressed { x, y: _ } => Ok(Scalar::from_repr(*x).unwrap().eq(&r)),
+        Coordinates::Identity => Ok(false),
         _ => unreachable!("Point is uncompressed"),
     }
 }
```
