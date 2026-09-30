# [?] fix(ssa_fuzzer): fix panic if compiler removed return value (#9216)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-07-16
Source: https://github.com/noir-lang/noir/commit/e6ccc3ed37408fdab6a6d5e2af11da981409acc1
Type: security-commit

## Details
fix(ssa_fuzzer): fix panic if compiler removed return value (#9216)

## Patch
### tooling/ssa_fuzzer/src/runner.rs
```diff
@@ -29,34 +29,46 @@ pub fn run_and_compare(
 
     let return_witnesses_acir = &acir_program.functions[0].return_values;
     let return_witnesses_brillig = &brillig_program.functions[0].return_values;
-    assert_eq!(return_witnesses_acir.0.len(), 1, "Multiple return value witnesses encountered");
-    assert_eq!(return_witnesses_brillig.0.len(), 1, "Multiple return value witnesses encountered");
-    let return_witness_acir: &Witness = return_witnesses_acir.0.first().unwrap();
-    let return_witness_brillig: &Witness = return_witnesses_brillig.0.first().unwrap();
+    assert!(return_witnesses_acir.0.len() <= 1, "Multiple return value witnesses encountered");
+    assert!(return_witnesses_brillig.0.len() <= 1, "Multiple return value witnesses encountered");
+    let return_witness_acir: Option<&Witness> = return_witnesses_acir.0.first();
+    let return_witness_brillig: Option<&Witness> = return_witnesses_brillig.0.first();
 
     // we found bug in case of
     // 1) acir_result != brillig_result
     // 2) acir execution failed, brillig execution succeeded
     // 3) acir execution succeeded, brillig execution failed
-    // it has depth 2, because nargo can panic or return NargoError
     match (acir_result, brillig_result) {
         (Ok(acir_result), Ok(brillig_result)) => {
-            let acir_result = acir_result[return_witness_acir];
-            let brillig_result = brillig_result[return_witness_brillig];
+            // we assume that if execution for both modes succeeds both programs returned something
+            let acir_result = acir_result[return_witness_acir.unwrap()];
+            let brillig_result = brillig_result[return_witness_brillig.unwrap()];
             if acir_result == brillig_result {
                 CompareResults::Agree(acir_result)
             } else {
                 CompareResults::Disagree(acir_result, brillig_result)
             }
         }
-        (Err(acir_error), Ok(brillig_result)) => {
-            let brillig_result = brillig_result[return_witness_brillig];
-            CompareResults::AcirFailed(acir_error.to_string(), brillig_result)
-        }
-        (Ok(acir_result), Err(brillig_error)) => {
-            let acir_result = acir_result[return_witness_acir];
-            CompareResults::BrilligFailed(brillig_error.to_string(), acir_result)
-        }
+        (Err(acir_error), Ok(brillig_result)) => match return_witness_brillig {
+            Some(return_witness) => {
+                let brillig_result = brillig_result[return_witness];
+                CompareResults::AcirFailed(acir_error.to_string(), brillig_result)
+            }
+            None => CompareResults::BothFailed(
+                acir_error.to_string(),
+                "Brillig program does not return anything".into(),
+            ),
+        },
+        (Ok(acir_result), Err(brillig_error)) => match return_witness_acir {
+            Some(return_witness) => {
+                let acir_result = acir_result[return_witness];
+                CompareResults::BrilligFailed(brillig_error.to_string(), acir_result)
+            }
+            None => CompareResults::BothFailed(
+                "ACIR program does not return anything".into(),
+                brillig_error.to_string(),
+            ),
+        },
         (Err(acir_error), Err(brillig_error)) => {
             CompareResults::BothFailed(acir_error.to_string(), brillig_error.to_string())
         }
```
