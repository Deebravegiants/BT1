# [?] Fix `BLS_G1_MSM`, `BLS_G2_MSM` and `BLS_PAIRING_CHECK` checks in `OOB` related to `cds` (#791)

## Summary
Severity: Unknown
Chain: Linea
Component: Consensys/linea-monorepo
Published: 2025-10-08
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/a4df90114ffa0b2b8c65d7d8a027705f26a6101a
Type: security-commit

## Details
Fix `BLS_G1_MSM`, `BLS_G2_MSM` and `BLS_PAIRING_CHECK` checks in `OOB` related to `cds` (#791)

Signed-off-by: Olivier Bégassat <38285177+OlivierBBB@users.noreply.github.com>
Co-authored-by: Olivier Bégassat <38285177+OlivierBBB@users.noreply.github.com>

## Patch
### blsdata/cancun/columns.lisp
```diff
@@ -3,7 +3,7 @@
 (defcolumns
   (STAMP        :i32)
   (ID           :i32)
-  (TOTAL_SIZE   :i16)
+  (TOTAL_SIZE   :i24)
   (INDEX        :i16)
   (INDEX_MAX    :i16)
   (LIMB         :i128)
```

### blsdata/prague/columns.lisp
```diff
@@ -3,7 +3,7 @@
 (defcolumns
   (STAMP        :i32)
   (ID           :i32)
-  (TOTAL_SIZE   :i16)
+  (TOTAL_SIZE   :i24)
   (INDEX        :i16)
   (INDEX_MAX    :i16)
   (LIMB         :i128)
```

### oob/cancun/precompiles/common/bls/bls_msm.lisp
```diff
@@ -21,6 +21,7 @@
                                                                         (* PRC_BLS_G2_MSM_MULTIPLICATION_COST  IS_BLS_G2_MSM)))
 (defun (prc-g1msm-prc-g2msm---remainder)                                               (shift OUTGOING_RES_LO 2))
 (defun (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)                        (shift OUTGOING_RES_LO 3))
+(defun (prc-g1msm-prc-g2msm---valid-cds)                                               (* (prc---cds-is-non-zero) (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)))
 (defun (prc-g1msm-prc-g2msm---num-inputs_msm-pair-size)                                (prc---cds))
 (defun (prc-g1msm-prc-g2msm---num-inputs-gt-128)                                       (shift OUTGOING_RES_LO 4))
 (defun (prc-g1msm-prc-g2msm---num-inputs-leq-128)                                      (- 1 (prc-g1msm-prc-g2msm---num-inputs-gt-128)))
@@ -42,7 +43,7 @@
   (call-to-ISZERO 3 0 (prc-g1msm-prc-g2msm---remainder)))
 
 (defconstraint prc-g1msm-prc-g2msm---compare-num-inputs-against-128 (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
-  (if-zero (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)
+  (if-zero (prc-g1msm-prc-g2msm---valid-cds)
            (noCall 4)
            (begin (vanishes! (shift ADD_FLAG 4))
                   (vanishes! (shift MOD_FLAG 4))
@@ -55,7 +56,7 @@
                   (eq! (shift [OUTGOING_DATA 4] 4) 128))))
 
 (defconstraint prc-g1-msm-prc-g2-msm---compute-discount (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
-  (if-zero (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)
+  (if-zero (prc-g1msm-prc-g2msm---valid-cds)
            (noCall 5)
            (if-not-zero (prc-g1msm-prc-g2msm---num-inputs-leq-128)
                     (begin (vanishes! (shift ADD_FLAG 5))
@@ -70,7 +71,7 @@
                     (begin (noCall 5)))))
 
 (defconstraint prc-g1msm-prc-g2msm---compute-precompile-cost-integer-division (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
-  (if-zero (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)
+  (if-zero (prc-g1msm-prc-g2msm---valid-cds)
            (noCall 6)
            (begin (vanishes! (shift ADD_FLAG 6))
                   (eq! (shift MOD_FLAG 6) 1)
@@ -83,7 +84,7 @@
                   (eq! (shift [OUTGOING_DATA 4] 6) PRC_BLS_MULTIPLICATION_MULTIPLIER))))
 
 (defconstraint prc-g1msm-prc-g2msm---compare-call-gas-against-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
-  (if-zero (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)
+  (if-zero (prc-g1msm-prc-g2msm---valid-cds)
            (noCall 7)
            (begin (vanishes! (shift ADD_FLAG 7))
                   (vanishes! (shift MOD_FLAG 7))
@@ -97,8 +98,8 @@
 
 (defconstraint prc-g1msm-prc-g2msm---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
   (begin (eq! (prc---hub-success)
-              (* (prc---cds-is-non-zero) (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size) (prc-g1msm-prc-g2msm---sufficient-gas)))
+              (* (prc-g1msm-prc-g2msm---valid-cds) (prc-g1msm-prc-g2msm---sufficient-gas)))
          (if-zero (prc---hub-success)
                   (vanishes! (prc---return-gas))
                   (eq! (prc---return-gas) 
-                       (- (prc---callee-gas) (prc-g1msm-prc-g2msm---precompile-cost))))))
\ No newline at end of file
+                       (- (prc---callee-gas) (prc-g1msm-prc-g2msm---precompile-cost))))))
```

### oob/cancun/precompiles/common/bls/bls_pairing_check.lisp
```diff
@@ -9,11 +9,12 @@
 
 (defun (prc-blspairingcheck---standard-precondition)                                   IS_BLS_PAIRING_CHECK)
 (defun (prc-blspairingcheck---remainder)                                               (shift OUTGOING_RES_LO 2))
-(defun (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)           (shift OUTGOING_RES_LO 3))
+(defun (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)          (shift OUTGOING_RES_LO 3))
+(defun (prc-blspairingcheck---valid-cds)                                               (* (prc---cds-is-non-zero) (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)))
 (defun (prc-blspairingcheck---insufficient-gas)                                        (shift OUTGOING_RES_LO 4))
 (defun (prc-blspairingcheck---sufficient-gas)                                          (- 1 (prc-blspairingcheck---insufficient-gas)))
-(defun (prc-blspairingcheck---precompile-cost_PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK)       (*    (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)
-                                                                  (+ (* GAS_CONST_BLS_PAIRING_CHECK PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK) (* GAS_CONST_BLS_PAIRING_CHECK_PAIR (prc---cds)))))
+(defun (prc-blspairingcheck---precompile-cost_PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK)       
+                                                                  (+ (* GAS_CONST_BLS_PAIRING_CHECK PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK) (* GAS_CONST_BLS_PAIRING_CHECK_PAIR (prc---cds))))
 
 (defconstraint prc-blspairingcheck---mod-cds-by-PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK (:guard (* (assumption---fresh-new-stamp) (prc-blspairingcheck---standard-precondition)))
   (call-to-MOD 2 0 (prc---cds) 0 PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK))
@@ -22,7 +23,7 @@
   (call-to-ISZERO 3 0 (prc-blspairingcheck---remainder)))
 
 (defconstraint prc-blspairingcheck---compare-call-gas-against-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-blspairingcheck---standard-precondition)))
-  (if-zero (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)
+  (if-zero (prc-blspairingcheck---valid-cds)
            (noCall 4)
            (begin (vanishes! (shift ADD_FLAG 4))
                   (vanishes! (shift MOD_FLAG 4))
@@ -37,7 +38,7 @@
 
 (defconstraint prc-blspairingcheck---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (prc-blspairingcheck---standard-precondition)))
   (begin (eq! (prc---hub-success)
-              (* (prc---cds-is-non-zero) (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size) (prc-blspairingcheck---sufficient-gas)))
+              (* (prc-blspairingcheck---valid-cds) (prc-blspairingcheck---sufficient-gas)))
          (if-zero (prc---hub-success)
                   (vanishes! (prc---return-gas))
                   (eq! (* (prc---return-gas) PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK)
```

### oob/osaka/precompiles/common/bls/bls_msm.lisp
```diff
@@ -20,16 +20,20 @@
                                                                     (+  (* PRC_BLS_G1_MSM_MULTIPLICATION_COST  IS_BLS_G1_MSM)
                                                                         (* PRC_BLS_G2_MSM_MULTIPLICATION_COST  IS_BLS_G2_MSM)))
 (defun (prc-g1msm-prc-g2msm---remainder)                                               (shift OUTGOING_RES_LO 2))
-(defun (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)                         (shift OUTGOING_RES_LO 3))
-(defun (prc-g1msm-prc-g2msm---num-inputs_msm-pair-size)                                 (prc---cds))
+(defun (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)                        (shift OUTGOING_RES_LO 3))
+(defun (prc-g1msm-prc-g2msm---valid-cds)                                               (* (prc---cds-is-non-zero) (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)))
+(defun (prc-g1msm-prc-g2msm---num-inputs_msm-pair-size)                                (prc---cds))
 (defun (prc-g1msm-prc-g2msm---num-inputs-gt-128)                                       (shift OUTGOING_RES_LO 4))
 (defun (prc-g1msm-prc-g2msm---num-inputs-leq-128)                                      (- 1 (prc-g1msm-prc-g2msm---num-inputs-gt-128)))
-(defun (prc-g1msm-prc-g2msm---discount)                                                (shift OUTGOING_RES_LO 5))
-(defun (prc-g1msm-prc-g2msm---insufficient-gas)                                        (shift OUTGOING_RES_LO 6))
+(defun (prc-g1msm-prc-g2msm---reference-table-discount)                                (shift OUTGOING_RES_LO 5)) 
+(defun (prc-g1msm-prc-g2msm---discount)                                                
+  (if-not-zero (prc-g1msm-prc-g2msm---num-inputs-leq-128) 
+                  (prc-g1msm-prc-g2msm---reference-table-discount) 
+                  (max-discount)))
+(defun (prc-g1msm-prc-g2msm---msm-cost-numerator_msm-pair-size)                        (* (prc-g1msm-prc-g2msm---num-inputs_msm-pair-size) (msm-multiplication-cost) (prc-g1msm-prc-g2msm---discount)))
+(defun (prc-g1msm-prc-g2msm---precompile-cost)                                         (shift OUTGOING_RES_LO 6))
+(defun (prc-g1msm-prc-g2msm---insufficient-gas)                                        (shift OUTGOING_RES_LO 7))
 (defun (prc-g1msm-prc-g2msm---sufficient-gas)                                          (- 1 (prc-g1msm-prc-g2msm---insufficient-gas)))
-(defun (prc-g1msm-prc-g2msm---precompile-cost_msm-pair-size_PRC_BLS_MULTIPLICATION_MULTIPLIER)       (* (prc-g1msm-prc-g2msm---num-inputs_msm-pair-size) (msm-multiplication-cost) (prc-g1msm-prc-g2msm---discount)))
-
-
 
 (defconstraint prc-g1msm-prc-g2msm---mod-cds-by-msm-pair-size (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
   (call-to-MOD 2 0 (prc---cds) 0 (msm-pair-size)))
@@ -38,7 +42,7 @@
   (call-to-ISZERO 3 0 (prc-g1msm-prc-g2msm---remainder)))
 
 (defconstraint prc-g1msm-prc-g2msm---compare-num-inputs-against-128 (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
-  (if-zero (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)
+  (if-zero (prc-g1msm-prc-g2msm---valid-cds)
            (noCall 4)
            (begin (vanishes! (shift ADD_FLAG 4))
                   (vanishes! (shift MOD_FLAG 4))
@@ -51,7 +55,7 @@
                   (eq! (shift [OUTGOING_DATA 4] 4) 128))))
 
 (defconstraint prc-g1-msm-prc-g2-msm---compute-discount (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
-  (if-zero (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)
+  (if-zero (prc-g1msm-prc-g2msm---valid-cds)
            (noCall 5)
            (if-not-zero (prc-g1msm-prc-g2msm---num-inputs-leq-128)
                     (begin (vanishes! (shift ADD_FLAG 5))
@@ -63,27 +67,38 @@
                            (vanishes! (shift [OUTGOING_DATA 2] 5))
                            (vanishes! (shift [OUTGOING_DATA 3] 5))
                            (vanishes! (shift [OUTGOING_DATA 4] 5)))
-                    (begin (noCall 5)
-                           (eq! (prc-g1msm-prc-g2msm---discount) (max-discount))))))
+                    (begin (noCall 5)))))
 
-(defconstraint prc-g1msm-prc-g2msm---compare-call-gas-against-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
-  (if-zero (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)
+(defconstraint prc-g1msm-prc-g2msm---compute-precompile-cost-integer-division (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
+  (if-zero (prc-g1msm-prc-g2msm---valid-cds)
            (noCall 6)
            (begin (vanishes! (shift ADD_FLAG 6))
-                  (vanishes! (shift MOD_FLAG 6))
-                  (eq! (shift WCP_FLAG 6) 1)
+                  (eq! (shift MOD_FLAG 6) 1)
+                  (vanishes! (shift WCP_FLAG 6))
                   (vanishes! (shift BLS_REF_TABLE_FLAG 6))
-                  (eq! (shift OUTGOING_INST 6) EVM_INST_LT)
+                  (eq! (shift OUTGOING_INST 6) EVM_INST_DIV)
                   (vanishes! (shift [OUTGOING_DATA 1] 6))
-                  (eq! (shift [OUTGOING_DATA 2] 6) (prc---callee-gas))
+                  (eq! (* (shift [OUTGOING_DATA 2] 6) (msm-pair-size)) (prc-g1msm-prc-g2msm---msm-cost-numerator_msm-pair-size))
                   (vanishes! (shift [OUTGOING_DATA 3] 6))
-                  (eq! (* (shift [OUTGOING_DATA 4] 6) (msm-pair-size) PRC_BLS_MULTIPLICATION_MULTIPLIER)
-                       (prc-g1msm-prc-g2msm---precompile-cost_msm-pair-size_PRC_BLS_MULTIPLICATION_MULTIPLIER)))))
+                  (eq! (shift [OUTGOING_DATA 4] 6) PRC_BLS_MULTIPLICATION_MULTIPLIER))))
+
+(defconstraint prc-g1msm-prc-g2msm---compare-call-gas-against-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
+  (if-zero (prc-g1msm-prc-g2msm---valid-cds)
+           (noCall 7)
+           (begin (vanishes! (shift ADD_FLAG 7))
+                  (vanishes! (shift MOD_FLAG 7))
+                  (eq! (shift WCP_FLAG 7) 1)
+                  (vanishes! (shift BLS_REF_TABLE_FLAG 7))
+                  (eq! (shift OUTGOING_INST 7) EVM_INST_LT)
+                  (vanishes! (shift [OUTGOING_DATA 1] 7))
+                  (eq! (shift [OUTGOING_DATA 2] 7) (prc---callee-gas))
+                  (vanishes! (shift [OUTGOING_DATA 3] 7))
+                  (eq! (shift [OUTGOING_DATA 4] 7) (prc-g1msm-prc-g2msm---precompile-cost)))))
 
 (defconstraint prc-g1msm-prc-g2msm---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
   (begin (eq! (prc---hub-success)
-              (* (prc---cds-is-non-zero) (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size) (prc-g1msm-prc-g2msm---sufficient-gas)))
+              (* (prc-g1msm-prc-g2msm---valid-cds) (prc-g1msm-prc-g2msm---sufficient-gas)))
          (if-zero (prc---hub-success)
                   (vanishes! (prc---return-gas))
-                  (eq! (* (prc---return-gas) (msm-pair-size) PRC_BLS_MULTIPLICATION_MULTIPLIER)
-                       (- (* (prc---callee-gas) (msm-pair-size) PRC_BLS_MULTIPLICATION_MULTIPLIER) (prc-g1msm-prc-g2msm---precompile-cost_msm-pair-size_PRC_BLS_MULTIPLICATION_MULTIPLIER))))))
+                  (eq! (prc---return-gas) 
+                       (- (prc---callee-gas) (prc-g1msm-prc-g2msm---precompile-cost))))))
```

### oob/osaka/precompiles/common/bls/bls_pairing_check.lisp
```diff
@@ -9,11 +9,12 @@
 
 (defun (prc-blspairingcheck---standard-precondition)                                   IS_BLS_PAIRING_CHECK)
 (defun (prc-blspairingcheck---remainder)                                               (shift OUTGOING_RES_LO 2))
-(defun (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)           (shift OUTGOING_RES_LO 3))
+(defun (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)          (shift OUTGOING_RES_LO 3))
+(defun (prc-blspairingcheck---valid-cds)                                               (* (prc---cds-is-non-zero) (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)))
 (defun (prc-blspairingcheck---insufficient-gas)                                        (shift OUTGOING_RES_LO 4))
 (defun (prc-blspairingcheck---sufficient-gas)                                          (- 1 (prc-blspairingcheck---insufficient-gas)))
-(defun (prc-blspairingcheck---precompile-cost_PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK)       (*    (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)
-                                                                  (+ (* GAS_CONST_BLS_PAIRING_CHECK PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK) (* GAS_CONST_BLS_PAIRING_CHECK_PAIR (prc---cds)))))
+(defun (prc-blspairingcheck---precompile-cost_PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK)       
+                                                                  (+ (* GAS_CONST_BLS_PAIRING_CHECK PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK) (* GAS_CONST_BLS_PAIRING_CHECK_PAIR (prc---cds))))
 
 (defconstraint prc-blspairingcheck---mod-cds-by-PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK (:guard (* (assumption---fresh-new-stamp) (prc-blspairingcheck---standard-precondition)))
   (call-to-MOD 2 0 (prc---cds) 0 PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK))
@@ -22,7 +23,7 @@
   (call-to-ISZERO 3 0 (prc-blspairingcheck---remainder)))
 
 (defconstraint prc-blspairingcheck---compare-call-gas-against-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-blspairingcheck---standard-precondition)))
-  (if-zero (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)
+  (if-zero (prc-blspairingcheck---valid-cds)
            (noCall 4)
            (begin (vanishes! (shift ADD_FLAG 4))
                   (vanishes! (shift MOD_FLAG 4))
@@ -37,7 +38,7 @@
 
 (defconstraint prc-blspairingcheck---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (prc-blspairingcheck---standard-precondition)))
   (begin (eq! (prc---hub-success)
-              (* (prc---cds-is-non-zero) (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size) (prc-blspairingcheck---sufficient-gas)))
+              (* (prc-blspairingcheck---valid-cds) (prc-blspairingcheck---sufficient-gas)))
          (if-zero (prc---hub-success)
                   (vanishes! (prc---return-gas))
                   (eq! (* (prc---return-gas) PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK)
```

### oob/prague/precompiles/common/bls/bls_msm.lisp
```diff
@@ -21,6 +21,7 @@
                                                                         (* PRC_BLS_G2_MSM_MULTIPLICATION_COST  IS_BLS_G2_MSM)))
 (defun (prc-g1msm-prc-g2msm---remainder)                                               (shift OUTGOING_RES_LO 2))
 (defun (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)                        (shift OUTGOING_RES_LO 3))
+(defun (prc-g1msm-prc-g2msm---valid-cds)                                               (* (prc---cds-is-non-zero) (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)))
 (defun (prc-g1msm-prc-g2msm---num-inputs_msm-pair-size)                                (prc---cds))
 (defun (prc-g1msm-prc-g2msm---num-inputs-gt-128)                                       (shift OUTGOING_RES_LO 4))
 (defun (prc-g1msm-prc-g2msm---num-inputs-leq-128)                                      (- 1 (prc-g1msm-prc-g2msm---num-inputs-gt-128)))
@@ -29,8 +30,7 @@
   (if-not-zero (prc-g1msm-prc-g2msm---num-inputs-leq-128) 
                   (prc-g1msm-prc-g2msm---reference-table-discount) 
                   (max-discount)))
-(defun (prc-g1msm-prc-g2msm---msm-cost-numerator_msm-pair-size)                        
-  (* (prc-g1msm-prc-g2msm---num-inputs_msm-pair-size) (msm-multiplication-cost) (prc-g1msm-prc-g2msm---discount)))
+(defun (prc-g1msm-prc-g2msm---msm-cost-numerator_msm-pair-size)                        (* (prc-g1msm-prc-g2msm---num-inputs_msm-pair-size) (msm-multiplication-cost) (prc-g1msm-prc-g2msm---discount)))
 (defun (prc-g1msm-prc-g2msm---precompile-cost)                                         (shift OUTGOING_RES_LO 6))
 (defun (prc-g1msm-prc-g2msm---insufficient-gas)                                        (shift OUTGOING_RES_LO 7))
 (defun (prc-g1msm-prc-g2msm---sufficient-gas)                                          (- 1 (prc-g1msm-prc-g2msm---insufficient-gas)))
@@ -42,7 +42,7 @@
   (call-to-ISZERO 3 0 (prc-g1msm-prc-g2msm---remainder)))
 
 (defconstraint prc-g1msm-prc-g2msm---compare-num-inputs-against-128 (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
-  (if-zero (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)
+  (if-zero (prc-g1msm-prc-g2msm---valid-cds)
            (noCall 4)
            (begin (vanishes! (shift ADD_FLAG 4))
                   (vanishes! (shift MOD_FLAG 4))
@@ -55,7 +55,7 @@
                   (eq! (shift [OUTGOING_DATA 4] 4) 128))))
 
 (defconstraint prc-g1-msm-prc-g2-msm---compute-discount (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
-  (if-zero (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)
+  (if-zero (prc-g1msm-prc-g2msm---valid-cds)
            (noCall 5)
            (if-not-zero (prc-g1msm-prc-g2msm---num-inputs-leq-128)
                     (begin (vanishes! (shift ADD_FLAG 5))
@@ -70,7 +70,7 @@
                     (begin (noCall 5)))))
 
 (defconstraint prc-g1msm-prc-g2msm---compute-precompile-cost-integer-division (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
-  (if-zero (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)
+  (if-zero (prc-g1msm-prc-g2msm---valid-cds)
            (noCall 6)
            (begin (vanishes! (shift ADD_FLAG 6))
                   (eq! (shift MOD_FLAG 6) 1)
@@ -83,7 +83,7 @@
                   (eq! (shift [OUTGOING_DATA 4] 6) PRC_BLS_MULTIPLICATION_MULTIPLIER))))
 
 (defconstraint prc-g1msm-prc-g2msm---compare-call-gas-against-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
-  (if-zero (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size)
+  (if-zero (prc-g1msm-prc-g2msm---valid-cds)
            (noCall 7)
            (begin (vanishes! (shift ADD_FLAG 7))
                   (vanishes! (shift MOD_FLAG 7))
@@ -97,7 +97,7 @@
 
 (defconstraint prc-g1msm-prc-g2msm---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (prc-g1msm-prc-g2msm---standard-precondition)))
   (begin (eq! (prc---hub-success)
-              (* (prc---cds-is-non-zero) (prc-g1msm-prc-g2msm---cds-is-multiple-of-msm-pair-size) (prc-g1msm-prc-g2msm---sufficient-gas)))
+              (* (prc-g1msm-prc-g2msm---valid-cds) (prc-g1msm-prc-g2msm---sufficient-gas)))
          (if-zero (prc---hub-success)
                   (vanishes! (prc---return-gas))
                   (eq! (prc---return-gas) 
```

### oob/prague/precompiles/common/bls/bls_pairing_check.lisp
```diff
@@ -9,11 +9,12 @@
 
 (defun (prc-blspairingcheck---standard-precondition)                                   IS_BLS_PAIRING_CHECK)
 (defun (prc-blspairingcheck---remainder)                                               (shift OUTGOING_RES_LO 2))
-(defun (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)           (shift OUTGOING_RES_LO 3))
+(defun (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)          (shift OUTGOING_RES_LO 3))
+(defun (prc-blspairingcheck---valid-cds)                                               (* (prc---cds-is-non-zero) (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)))
 (defun (prc-blspairingcheck---insufficient-gas)                                        (shift OUTGOING_RES_LO 4))
 (defun (prc-blspairingcheck---sufficient-gas)                                          (- 1 (prc-blspairingcheck---insufficient-gas)))
-(defun (prc-blspairingcheck---precompile-cost_PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK)       (*    (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)
-                                                                  (+ (* GAS_CONST_BLS_PAIRING_CHECK PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK) (* GAS_CONST_BLS_PAIRING_CHECK_PAIR (prc---cds)))))
+(defun (prc-blspairingcheck---precompile-cost_PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK)       
+                                                                  (+ (* GAS_CONST_BLS_PAIRING_CHECK PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK) (* GAS_CONST_BLS_PAIRING_CHECK_PAIR (prc---cds))))
 
 (defconstraint prc-blspairingcheck---mod-cds-by-PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK (:guard (* (assumption---fresh-new-stamp) (prc-blspairingcheck---standard-precondition)))
   (call-to-MOD 2 0 (prc---cds) 0 PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK))
@@ -22,7 +23,7 @@
   (call-to-ISZERO 3 0 (prc-blspairingcheck---remainder)))
 
 (defconstraint prc-blspairingcheck---compare-call-gas-against-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-blspairingcheck---standard-precondition)))
-  (if-zero (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size)
+  (if-zero (prc-blspairingcheck---valid-cds)
            (noCall 4)
            (begin (vanishes! (shift ADD_FLAG 4))
                   (vanishes! (shift MOD_FLAG 4))
@@ -37,7 +38,7 @@
 
 (defconstraint prc-blspairingcheck---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (prc-blspairingcheck---standard-precondition)))
   (begin (eq! (prc---hub-success)
-              (* (prc---cds-is-non-zero) (prc-blspairingcheck---cds-is-multiple-of-bls-pairing-check-pair-size) (prc-blspairingcheck---sufficient-gas)))
+              (* (prc-blspairingcheck---valid-cds) (prc-blspairingcheck---sufficient-gas)))
          (if-zero (prc---hub-success)
                   (vanishes! (prc---return-gas))
                   (eq! (* (prc---return-gas) PRECOMPILE_CALL_DATA_UNIT_SIZE___BLS_PAIRING_CHECK)
```
