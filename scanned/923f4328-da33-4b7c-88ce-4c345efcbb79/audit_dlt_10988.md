# [?] fix: verifier dos (#1017)

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2024-07-02
Source: https://github.com/succinctlabs/sp1/commit/9bf3f414f4648f4c36c57b81a7fb71bc454efd85
Type: security-commit

## Details
fix: verifier dos (#1017)

## Patch
### Cargo.lock
```diff
@@ -4972,8 +4972,10 @@ dependencies = [
  "indicatif",
  "log",
  "num-bigint 0.4.6",
+ "p3-baby-bear",
  "p3-commit",
  "p3-field",
+ "p3-fri",
  "p3-matrix",
  "prost",
  "reqwest 0.12.5",
```

### core/src/stark/verifier.rs
```diff
@@ -51,7 +51,9 @@ impl<SC: StarkGenericConfig, A: MachineAir<Val<SC>>> Verifier<SC, A> {
 
         let pcs = config.pcs();
 
-        assert_eq!(chips.len(), opened_values.chips.len());
+        if chips.len() != opened_values.chips.len() {
+            return Err(VerificationError::ChipOpeningLengthMismatch);
+        }
 
         let log_degrees = opened_values
             .chips
@@ -417,6 +419,7 @@ pub enum VerificationError<SC: StarkGenericConfig> {
     /// The shape of the opening arguments is invalid.
     OpeningShapeError(String, OpeningShapeError),
     MissingCpuChip,
+    ChipOpeningLengthMismatch,
 }
 
 impl Debug for OpeningShapeError {
@@ -483,6 +486,9 @@ impl<SC: StarkGenericConfig> Debug for VerificationError<SC> {
             VerificationError::MissingCpuChip => {
                 write!(f, "Missing CPU chip")
             }
+            VerificationError::ChipOpeningLengthMismatch => {
+                write!(f, "Chip opening length mismatch")
+            }
         }
     }
 }
@@ -502,6 +508,9 @@ impl<SC: StarkGenericConfig> Display for VerificationError<SC> {
             VerificationError::MissingCpuChip => {
                 write!(f, "Missing CPU chip in shard")
             }
+            VerificationError::ChipOpeningLengthMismatch => {
+                write!(f, "Chip opening length mismatch")
+            }
         }
     }
 }
```
