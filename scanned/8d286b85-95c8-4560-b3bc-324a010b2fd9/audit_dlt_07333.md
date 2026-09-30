# [?] fix(oob): modexp extract and blake params (#360)

## Summary
Severity: Unknown
Chain: Linea
Component: Consensys/linea-monorepo
Published: 2024-09-17
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/6dc315f0f9bf8d079711a0bed79ca37b8f2796f2
Type: security-commit

## Details
fix(oob): modexp extract and blake params (#360)

Signed-off-by: Olivier Bégassat <38285177+OlivierBBB@users.noreply.github.com>
Co-authored-by: Olivier Bégassat <38285177+OlivierBBB@users.noreply.github.com>

## Patch
### oob/constraints.lisp
```diff
@@ -306,7 +306,7 @@
 (defun (jump---jump-must-be-attempted)      [DATA 8])
 (defun (jump---valid-pc-new)                OUTGOING_RES_LO)
 
-(defconstraint jump---compare-pc-new-and-code-size (:guard (* (assumption---fresh-new-stamp) (jump---standard-precondition)))
+(defconstraint jump---compare-pc-new-against-code-size (:guard (* (assumption---fresh-new-stamp) (jump---standard-precondition)))
   (call-to-LT 0 (jump---pc-new-hi) (jump---pc-new-lo) 0 (jump---code-size)))
 
 (defconstraint jump---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (jump---standard-precondition)))
@@ -334,7 +334,7 @@
 (defun (jumpi---valid-pc-new)               OUTGOING_RES_LO)
 (defun (jumpi---jump-cond-is-zero)          (next OUTGOING_RES_LO))
 
-(defconstraint jumpi---compare-pc-new-and-code-size (:guard (* (assumption---fresh-new-stamp) (jumpi---standard-precondition)))
+(defconstraint jumpi---compare-pc-new-against-code-size (:guard (* (assumption---fresh-new-stamp) (jumpi---standard-precondition)))
   (call-to-LT 0 (jumpi---pc-new-hi) (jumpi---pc-new-lo) 0 (jumpi---code-size)))
 
 (defconstraint jumpi---check-jump-cond-is-zero (:guard (* (assumption---fresh-new-stamp) (jumpi---standard-precondition)))
@@ -380,7 +380,7 @@
            (call-to-ADD 1 0 (rdc---offset-lo) 0 (rdc---size-lo))
            (noCall 1)))
 
-(defconstraint rdc---compare-offset-and-size-sum-and-rds (:guard (* (assumption---fresh-new-stamp) (rdc---standard-precondition)))
+(defconstraint rdc---compare-offset-plus-size-against-rds (:guard (* (assumption---fresh-new-stamp) (rdc---standard-precondition)))
   (if-zero (rdc---rdc-roob)
            (begin (vanishes! (shift ADD_FLAG 2))
                   (vanishes! (shift MOD_FLAG 2))
@@ -410,7 +410,7 @@
 (defun (cdl---cdl-out-of-bounds)        [DATA 7])
 (defun (cdl---touches-ram)              OUTGOING_RES_LO)
 
-(defconstraint cdl---compare-offset-and-cds (:guard (* (assumption---fresh-new-stamp) (cdl---standard-precondition)))
+(defconstraint cdl---compare-offset-against-cds (:guard (* (assumption---fresh-new-stamp) (cdl---standard-precondition)))
   (call-to-LT 0 (cdl---offset-hi) (cdl---offset-lo) 0 (cdl---cds)))
 
 (defconstraint cdl---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (cdl---standard-precondition)))
@@ -427,7 +427,7 @@
 (defun (sstore---sstorex)                   [DATA 7])
 (defun (sstore---sufficient-gas)            OUTGOING_RES_LO)
 
-(defconstraint sstore---compare-g-call-stipend-and-gas (:guard (* (assumption---fresh-new-stamp) (sstore---standard-precondition)))
+(defconstraint sstore---compare-g-call-stipend-against-gas (:guard (* (assumption---fresh-new-stamp) (sstore---standard-precondition)))
   (call-to-LT 0 0 GAS_CONST_G_CALL_STIPEND 0 (sstore---gas)))
 
 (defconstraint sstore---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (sstore---standard-precondition)))
@@ -447,7 +447,7 @@
 (defun (deployment---max-code-size-exception)          [DATA 7])
 (defun (deployment---exceeds-max-code-size)            OUTGOING_RES_LO)
 
-(defconstraint deployment---compare-24576-and-code-size (:guard (* (assumption---fresh-new-stamp) (deployment---standard-precondition)))
+(defconstraint deployment---compare-24576-against-code-size (:guard (* (assumption---fresh-new-stamp) (deployment---standard-precondition)))
   (call-to-LT 0 0 24576 (deployment---code-size-hi) (deployment---code-size-lo)))
 
 (defconstraint deployment---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (deployment---standard-precondition)))
@@ -491,10 +491,10 @@
 (defun (call---call-stack-depth-abort)          (- 1 (next OUTGOING_RES_LO)))
 (defun (call---value-is-zero)                   (shift OUTGOING_RES_LO 2))
 
-(defconstraint call---compare-balance-and-value (:guard (* (assumption---fresh-new-stamp) (call---standard-precondition)))
+(defconstraint call---compare-balance-against-value (:guard (* (assumption---fresh-new-stamp) (call---standard-precondition)))
   (call-to-LT 0 0 (call---balance) (call---value-hi) (call---value-lo)))
 
-(defconstraint call---compare-call-stack-depth-and-1024 (:guard (* (assumption---fresh-new-stamp) (call---standard-precondition)))
+(defconstraint call---compare-call-stack-depth-against-1024 (:guard (* (assumption---fresh-new-stamp) (call---standard-precondition)))
   (call-to-LT 1 0 (call---call-stack-depth) 0 1024))
 
 (defconstraint call---check-value-is-zero (:guard (* (assumption---fresh-new-stamp) (call---standard-precondition)))
@@ -528,16 +528,16 @@
 (defun (create---creator-nonce-abort)                  (- 1 (shift OUTGOING_RES_LO 3)))
 (defun (create---aborting-conditions-sum)              (+ (create---insufficient-balance-abort) (create---stack-depth-abort) (create---creator-nonce-abort)))
 
-(defconstraint create---compare-balance-and-value (:guard (* (assumption---fresh-new-stamp) (create---standard-precondition)))
+(defconstraint create---compare-balance-against-value (:guard (* (assumption---fresh-new-stamp) (create---standard-precondition)))
   (call-to-LT 0 0 (create---balance) (create---value-hi) (create---value-lo)))
 
-(defconstraint create---compare-call-stack-depth-and-1024 (:guard (* (assumption---fresh-new-stamp) (create---standard-precondition)))
+(defconstraint create---compare-call-stack-depth-against-1024 (:guard (* (assumption---fresh-new-stamp) (create---standard-precondition)))
   (call-to-LT 1 0 (create---call-stack-depth) 0 1024))
 
 (defconstraint create---check-nonce-is-zero (:guard (* (assumption---fresh-new-stamp) (create---standard-precondition)))
   (call-to-ISZERO 2 0 (create---nonce)))
 
-(defconstraint create---compare-creator-nonce-and-max-nonce (:guard (* (assumption---fresh-new-stamp) (create---standard-precondition)))
+(defconstraint create---compare-creator-nonce-against-max-nonce (:guard (* (assumption---fresh-new-stamp) (create---standard-precondition)))
   (call-to-LT 3 0 (create---creator-nonce) 0 EIP2681_MAX_NONCE))
 
 (defconstraint create---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (create---standard-precondition)))
@@ -597,7 +597,7 @@
 (defun (prc-ecrecover-prc-ecadd-prc-ecmul---precompile-cost)          (+ (* 3000 IS_ECRECOVER) (* 150 IS_ECADD) (* 6000 IS_ECMUL)))
 (defun (prc-ecrecover-prc-ecadd-prc-ecmul---insufficient-gas)         (shift OUTGOING_RES_LO 2))
 
-(defconstraint prc-ecrecover-prc-ecadd-prc-ecmul---compare-call-gas-and-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-ecrecover-prc-ecadd-prc-ecmul---standard-precondition)))
+(defconstraint prc-ecrecover-prc-ecadd-prc-ecmul---compare-call-gas-against-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-ecrecover-prc-ecadd-prc-ecmul---standard-precondition)))
   (call-to-LT 2 0 (prc---call-gas) 0 (prc-ecrecover-prc-ecadd-prc-ecmul---precompile-cost)))
 
 (defconstraint prc-ecrecover-prc-ecadd-prc-ecmul---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (prc-ecrecover-prc-ecadd-prc-ecmul---standard-precondition)))
@@ -622,7 +622,7 @@
 (defconstraint prc-sha2-prc-ripemd-prc-identity---div-cds-plus-31-by-32 (:guard (* (assumption---fresh-new-stamp) (prc-sha2-prc-ripemd-prc-identity---standard-precondition)))
   (call-to-DIV 2 0 (+ (prc---cds) 31) 0 32))
 
-(defconstraint prc-sha2-prc-ripemd-prc-identity---compare-call-gas-and-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-sha2-prc-ripemd-prc-identity---standard-precondition)))
+(defconstraint prc-sha2-prc-ripemd-prc-identity---compare-call-gas-against-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-sha2-prc-ripemd-prc-identity---standard-precondition)))
   (call-to-LT 3 0 (prc---call-gas) 0 (prc-sha2-prc-ripemd-prc-identity---precompile-cost)))
 
 (defconstraint prc-sha2-prc-ripemd-prc-identity---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (prc-sha2-prc-ripemd-prc-identity---standard-precondition)))
@@ -651,7 +651,7 @@
 (defconstraint prc-ecpairing---check-remainder-is-zero (:guard (* (assumption---fresh-new-stamp) (prc-ecpairing---standard-precondition)))
   (call-to-ISZERO 3 0 (prc-ecpairing---remainder)))
 
-(defconstraint prc-ecpairing---compare-call-gas-and-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-ecpairing---standard-precondition)))
+(defconstraint prc-ecpairing---compare-call-gas-against-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-ecpairing---standard-precondition)))
   (if-zero (prc-ecpairing---is-multiple_192)
            (noCall 4)
            (begin (vanishes! (shift ADD_FLAG 4))
@@ -689,13 +689,13 @@
 (defun (prc-modexp-cds---extract-ebs)              [DATA 4])
 (defun (prc-modexp-cds---extract-mbs)              [DATA 5])
 
-(defconstraint prc-modexp-cds---compare-0-and-cds (:guard (* (assumption---fresh-new-stamp) (prc-modexp-cds---standard-precondition)))
+(defconstraint prc-modexp-cds---compare-0-against-cds (:guard (* (assumption---fresh-new-stamp) (prc-modexp-cds---standard-precondition)))
   (call-to-LT 0 0 0 0 (prc---cds)))
 
-(defconstraint prc-modexp-cds---compare-32-and-cds (:guard (* (assumption---fresh-new-stamp) (prc-modexp-cds---standard-precondition)))
+(defconstraint prc-modexp-cds---compare-32-against-cds (:guard (* (assumption---fresh-new-stamp) (prc-modexp-cds---standard-precondition)))
   (call-to-LT 1 0 32 0 (prc---cds)))
 
-(defconstraint prc-modexp-cds---compare-64-and-cds (:guard (* (assumption---fresh-new-stamp) (prc-modexp-cds---standard-precondition)))
+(defconstraint prc-modexp-cds---compare-64-against-cds (:guard (* (assumption---fresh-new-stamp) (prc-modexp-cds---standard-precondition)))
   (call-to-LT 2 0 64 0 (prc---cds)))
 
 (defconstraint prc-modexp-cds---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (prc-modexp-cds---standard-precondition)))
@@ -719,10 +719,10 @@
 (defun (prc-modexp-xbs---compo-to_512)             OUTGOING_RES_LO)
 (defun (prc-modexp-xbs---comp)                     (next OUTGOING_RES_LO))
 
-(defconstraint prc-modexp-xbs---compare-xbs-hi-and-513 (:guard (* (assumption---fresh-new-stamp) (prc-modexp-xbs---standard-precondition)))
+(defconstraint prc-modexp-xbs---compare-xbs-hi-against-513 (:guard (* (assumption---fresh-new-stamp) (prc-modexp-xbs---standard-precondition)))
   (call-to-LT 0 (prc-modexp-xbs---xbs-hi) (prc-modexp-xbs---xbs-lo) 0 513))
 
-(defconstraint prc-modexp-xbs---compare-xbs-and-ybs (:guard (* (assumption---fresh-new-stamp) (prc-modexp-xbs---standard-precondition)))
+(defconstraint prc-modexp-xbs---compare-xbs-against-ybs (:guard (* (assumption---fresh-new-stamp) (prc-modexp-xbs---standard-precondition)))
   (call-to-LT 1 0 (prc-modexp-xbs---xbs-lo) 0 (prc-modexp-xbs---ybs-lo)))
 
 (defconstraint prc-modexp-xbs---check-xbs-is-zero (:guard (* (assumption---fresh-new-stamp) (prc-modexp-xbs---standard-precondition)))
@@ -763,13 +763,13 @@
 (defconstraint prc-modexp-lead---check-ebs-is-zero (:guard (* (assumption---fresh-new-stamp) (prc-modexp-lead---standard-precondition)))
   (call-to-ISZERO 0 0 (prc-modexp-lead---ebs)))
 
-(defconstraint prc-modexp-lead---compare-ebs-and-32 (:guard (* (assumption---fresh-new-stamp) (prc-modexp-lead---standard-precondition)))
+(defconstraint prc-modexp-lead---compare-ebs-against-32 (:guard (* (assumption---fresh-new-stamp) (prc-modexp-lead---standard-precondition)))
   (call-to-LT 1 0 (prc-modexp-lead---ebs) 0 32))
 
-(defconstraint prc-modexp-lead---compare-ebs-and-cds (:guard (* (assumption---fresh-new-stamp) (prc-modexp-lead---standard-precondition)))
+(defconstraint prc-modexp-lead---compare-ebs-against-cds (:guard (* (assumption---fresh-new-stamp) (prc-modexp-lead---standard-precondition)))
   (call-to-LT 2 0 (+ 96 (prc-modexp-lead---bbs)) 0 (prc---cds)))
 
-(defconstraint prc-modexp-lead---compare-cds-minus-96-plus-bbs-and-32 (:guard (* (assumption---fresh-new-stamp) (prc-modexp-lead---standard-precondition)))
+(defconstraint prc-modexp-lead---compare-cds-minus-96-plus-bbs-against-32 (:guard (* (assumption---fresh-new-stamp) (prc-modexp-lead---standard-precondition)))
   (if-not-zero (prc-modexp-lead---call-data-contains-exponent-bytes)
                (call-to-LT 3
                            0
@@ -830,10 +830,10 @@
 (defconstraint prc-modexp-pricing---div-big-numerator-by-quaddivisor (:guard (* (assumption---fresh-new-stamp) (prc-modexp-pricing---standard-precondition)))
   (call-to-DIV 3 0 (prc-modexp-pricing---big-numerator) 0 G_QUADDIVISOR))
 
-(defconstraint prc-modexp-pricing---compare-big-quotient-and-200 (:guard (* (assumption---fresh-new-stamp) (prc-modexp-pricing---standard-precondition)))
+(defconstraint prc-modexp-pricing---compare-big-quotient-against-200 (:guard (* (assumption---fresh-new-stamp) (prc-modexp-pricing---standard-precondition)))
   (call-to-LT 4 0 (prc-modexp-pricing---big-quotient) 0 200))
 
-(defconstraint prc-modexp-pricing---compare-call-gas-and-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-modexp-pricing---standard-precondition)))
+(defconstraint prc-modexp-pricing---compare-call-gas-against-precompile-cost (:guard (* (assumption---fresh-new-stamp) (prc-modexp-pricing---standard-precondition)))
   (call-to-LT 5 0 (prc---call-gas) 0 (prc-modexp-pricing---precompile-cost)))
 
 (defconstraint prc-modexp-pricing---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (prc-modexp-pricing---standard-precondition)))
@@ -871,6 +871,9 @@
 (defconstraint prc-modexp-extract---check-mbs-is-zero (:guard (* (assumption---fresh-new-stamp) (prc-modexp-extract---standard-precondition)))
   (call-to-ISZERO 2 0 (prc-modexp-extract---mbs)))
 
+(defconstraint prc-modexp-extract---compare-96-plus-bbs-plus-ebs-against-cds (:guard (* (assumption---fresh-new-stamp) (prc-modexp-extract---standard-precondition)))
+  (call-to-LT 3 0 (+ 96 (prc-modexp-extract---bbs) (prc-modexp-extract---ebs)) 0 (prc---cds)))
+
 (defconstraint prc-modexp-extract---justify-hub-predictions (:guard (* (assumption---fresh-new-stamp) (prc-modexp-extract---standard-precondition)))
   (begin (eq! (prc-modexp-extract---extract-modulus)
               (* (prc-modexp-extract---call-data-extends-beyond-exponent)
@@ -896,7 +899,7 @@
 (defun (prc-blake-cds---valid-cds)  OUTGOING_RES_LO)
 (defun (prc-blake-cds---r@c-is-zero)   (next OUTGOING_RES_LO))
 
-(defconstraint prc-blake-cds---compare-cds-and-213 (:guard (* (assumption---fresh-new-stamp) (prc-blake-cds---standard-precondition)))
+(defconstraint prc-blake-cds---compare-cds-against-213 (:guard (* (assumption---fresh-new-stamp) (prc-blake-cds---standard-precondition)))
   (call-to-EQ 0 0 (prc---cds) 0 213))
 
 (defconstraint prc-blake-cds---check--is-zero (:guard (* (assumption---fresh-new-stamp) (prc-blake-cds---standard-precondition)))
@@ -919,10 +922,10 @@
 (defun (prc-blake-params---f-is-a-bit)                     (next OUTGOING_RES_LO))
 
 
-(defconstraint prc-blake-params---compare-call-gas-and-blake-r (:guard (* (assumption---fresh-new-stamp) (prc-blake-params---standard-precondition)))
+(defconstraint prc-blake-params---compare-call-gas-against-blake-r (:guard (* (assumption---fresh-new-stamp) (prc-blake-params---standard-precondition)))
   (call-to-LT 0 0 (prc---call-gas) 0 (prc-blake-params---blake-r)))
 
-(defconstraint prc-blake-params---compare-blake-f-and-blake-f-square (:guard (* (assumption---fresh-new-stamp) (prc-blake-params---standard-precondition)))
+(defconstraint prc-blake-params---compare-blake-f-against-blake-f-square (:guard (* (assumption---fresh-new-stamp) (prc-blake-params---standard-precondition)))
   (call-to-EQ 1
               0
               (prc-blake-params---blake-f)
@@ -933,7 +936,7 @@
   (begin (eq! (prc---ram-success)
               (* (prc-blake-params---sufficient-gas) (prc-blake-params---f-is-a-bit)))
          (if-not-zero (prc---ram-success)
-                      (eq! (prc---return-gas) (- (prc---call-gas) (prc-blake-params---blake-f)))
+                      (eq! (prc---return-gas) (- (prc---call-gas) (prc-blake-params---blake-r)))
                       (vanishes! (prc---return-gas)))))
 
 
```
