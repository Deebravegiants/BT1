# [?] fix(oob): inst modexp pricing f of max (#320)

## Summary
Severity: Unknown
Chain: Linea
Component: Consensys/linea-monorepo
Published: 2024-09-04
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/7fe32e2761e3246628fc135dd5e3837e01ba1295
Type: security-commit

## Details
fix(oob): inst modexp pricing f of max (#320)

Signed-off-by: Olivier Bégassat <38285177+OlivierBBB@users.noreply.github.com>
Co-authored-by: Olivier Bégassat <38285177+OlivierBBB@users.noreply.github.com>

## Patch
### oob/constraints.lisp
```diff
@@ -804,7 +804,7 @@
 (defun (prc-modexp-pricing---exponent-log)            [DATA 6])
 (defun (prc-modexp-pricing---max-xbs-ybs)             [DATA 7])
 (defun (prc-modexp-pricing---exponent-log-is-zero)    (next OUTGOING_RES_LO))
-(defun (prc-modexp-pricing---f-of-max)                (shift OUTGOING_RES_LO 2))
+(defun (prc-modexp-pricing---f-of-max)                (*  (shift OUTGOING_RES_LO 2)  (shift OUTGOING_RES_LO 2)))
 (defun (prc-modexp-pricing---big-quotient)            (shift OUTGOING_RES_LO 3))
 (defun (prc-modexp-pricing---big-quotient_LT_200)     (shift OUTGOING_RES_LO 4))
 (defun (prc-modexp-pricing---big-numerator)           (if-zero (prc-modexp-pricing---exponent-log-is-zero)
@@ -820,10 +820,10 @@
 (defconstraint prc-modexp-pricing---check-exponent-log-is-zero (:guard (* (assumption---fresh-new-stamp) (prc-modexp-pricing---standard-precondition)))
   (call-to-ISZERO 1 0 (prc-modexp-pricing---exponent-log)))
 
-(defconstraint prc-modexp-pricing---div-max-xbs-ybs-square-plus-7-by-8 (:guard (* (assumption---fresh-new-stamp) (prc-modexp-pricing---standard-precondition)))
+(defconstraint prc-modexp-pricing---div-max-xbs-ybs-plus-7-by-8 (:guard (* (assumption---fresh-new-stamp) (prc-modexp-pricing---standard-precondition)))
   (call-to-DIV 2
                0
-               (+ (* (prc-modexp-pricing---max-xbs-ybs) (prc-modexp-pricing---max-xbs-ybs)) 7)
+               (+ (prc-modexp-pricing---max-xbs-ybs) 7)
                0
                8))
 
```
