# [?] Fix error display which would cause stack overflow

## Summary
Severity: Unknown
Chain: ZK
Component: zkcrypto/bellman
Published: 2021-12-09
Source: https://github.com/zkcrypto/bellman/commit/14a6e6db729fa93d8f69375174710866d36286f2
Type: security-commit

## Details
Fix error display which would cause stack overflow

## Patch
### src/lib.rs
```diff
@@ -327,9 +327,11 @@ impl From<io::Error> for SynthesisError {
     }
 }
 
-impl Error for SynthesisError {
-    fn description(&self) -> &str {
-        match *self {
+impl Error for SynthesisError {}
+
+impl fmt::Display for SynthesisError {
+    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> Result<(), fmt::Error> {
+        let msg = match *self {
             SynthesisError::AssignmentMissing => {
                 "an assignment for a variable could not be computed"
             }
@@ -339,17 +341,12 @@ impl Error for SynthesisError {
             SynthesisError::UnexpectedIdentity => "encountered an identity element in the CRS",
             SynthesisError::IoError(_) => "encountered an I/O error",
             SynthesisError::UnconstrainedVariable => "auxiliary variable was unconstrained",
-        }
-    }
-}
-
-impl fmt::Display for SynthesisError {
-    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> Result<(), fmt::Error> {
+        };
         if let SynthesisError::IoError(ref e) = *self {
             write!(f, "I/O error: ")?;
             e.fmt(f)
         } else {
-            write!(f, "{}", self)
+            write!(f, "{}", msg)
         }
     }
 }
@@ -363,18 +360,15 @@ pub enum VerificationError {
     InvalidProof,
 }
 
-impl Error for VerificationError {
-    fn description(&self) -> &str {
-        match *self {
-            VerificationError::InvalidVerifyingKey => "malformed verifying key",
-            VerificationError::InvalidProof => "proof verification failed",
-        }
-    }
-}
+impl Error for VerificationError {}
 
 impl fmt::Display for VerificationError {
     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> Result<(), fmt::Error> {
-        write!(f, "{}", self)
+        let msg = match *self {
+            VerificationError::InvalidVerifyingKey => "malformed verifying key",
+            VerificationError::InvalidProof => "proof verification failed",
+        };
+        write!(f, "{}", msg)
     }
 }
 
@@ -573,3 +567,31 @@ impl<'cs, Scalar: PrimeField, CS: ConstraintSystem<Scalar>> ConstraintSystem<Sca
         (**self).get_root()
     }
 }
+
+#[cfg(test)]
+mod test {
+    use super::*;
+
+    #[test]
+    fn verification_error_string() {
+        let err = VerificationError::InvalidProof;
+
+        // Make sure it correctly returns something (i.e. it's not an endless loop)
+        assert!(!err.to_string().is_empty());
+    }
+
+    #[test]
+    fn synthesis_error_string() {
+        let err = SynthesisError::PolynomialDegreeTooLarge;
+
+        // Make sure it correctly returns something (i.e. it's not an endless loop)
+        assert!(!err.to_string().is_empty());
+
+        let err = SynthesisError::IoError(io::Error::new(io::ErrorKind::Other, "other"));
+        assert!(
+            err.to_string().contains("other"),
+            "\"{}\" does not contain the underlying error",
+            err
+        );
+    }
+}
```
