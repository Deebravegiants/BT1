# [?] fix: prevent `bound_constraint_with_offset` from panicking (#9145)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-07-08
Source: https://github.com/noir-lang/noir/commit/c6ee7bae3f200014ec1ee688c7da2ce389a32172
Type: security-commit

## Details
fix: prevent `bound_constraint_with_offset` from panicking (#9145)

## Patch
### compiler/noirc_evaluator/src/acir/acir_context/mod.rs
```diff
@@ -1047,7 +1047,9 @@ impl<F: AcirField, B: BlackBoxFunctionSolver<F>> AcirContext<F, B> {
 
             let bit_size = bit_size_u128(rhs_offset);
             // r = 2^bit_size - rhs_offset -1, is of bit size  'bit_size' by construction
-            let r = (1_u128 << bit_size) - rhs_offset - 1;
+            let two_pow_bit_size_minus_one =
+                if bit_size == 128 { u128::MAX } else { (1_u128 << bit_size) - 1 };
+            let r = two_pow_bit_size_minus_one - rhs_offset;
             // however, since it is a constant, we can compute it's actual bit size
             let r_bit_size = bit_size_u128(r);
 
```

### tooling/ssa_executor/src/lib.rs
```diff
@@ -85,4 +85,56 @@ mod tests {
         let result = execute_ssa(ssa.to_string(), WitnessMap::new(), CompileOptions::default());
         assert!(result.is_err());
     }
+
+    #[test]
+    fn bound_constraint_with_offset_bug() {
+        let ssa_without_runtime = "
+            (inline) fn main f0 {
+              b0(v0: i32, v1: u1, v2: u1, v3: u1, v4: u1, v5: u1, v6: u1):
+                jmpif v6 then: b1, else: b2
+              b1():
+                v7 = cast v0 as u128
+                jmp b3()
+              b2():
+                jmp b9()
+              b3():
+                v8 = div v7, v7
+                jmp b4()
+              b4():
+                v9 = not v8
+                jmp b5()
+              b5():
+                v10 = add v8, v9
+                jmp b6()
+              b6():
+                v12 = div v9, v9
+                jmp b7()
+              b7():
+                v13 = div v12, v10
+                jmp b9()
+              b8():
+                v14 = cast v1 as Field
+                return v14
+              b9():
+                jmp b8()
+            }
+        ";
+        let acir_ssa = "acir".to_string() + ssa_without_runtime;
+        let brillig_ssa = "brillig".to_string() + ssa_without_runtime;
+        let mut witness_map = WitnessMap::new();
+        witness_map.insert(Witness(0), FieldElement::from(1188688178_u32));
+        for i in 1..6 {
+            witness_map.insert(Witness(i), FieldElement::from(1_u32));
+        }
+        witness_map.insert(Witness(6), FieldElement::from(0_u32));
+        let acir_result =
+            execute_ssa(acir_ssa.to_string(), witness_map.clone(), CompileOptions::default());
+        let brillig_result =
+            execute_ssa(brillig_ssa.to_string(), witness_map, CompileOptions::default());
+        match (acir_result, brillig_result) {
+            (Err(acir), Ok(_brillig)) => panic!("Acir failed with: {}, brillig succeeded", acir),
+            (Ok(_acir), Err(brillig)) => panic!("Acir succeeded, brillig failed: {}", brillig),
+            _ => {}
+        }
+    }
 }
```
