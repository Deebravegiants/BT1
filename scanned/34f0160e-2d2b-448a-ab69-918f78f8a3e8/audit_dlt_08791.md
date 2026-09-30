# [?] fix(oob): modexp lead constraints (#306)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2024-08-23
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/7c44dc562e588dbd7fbeadc81ff48337cd52ad66
Type: security-commit

## Details
fix(oob): modexp lead constraints (#306)

## Patch
### oob/constraints.lisp
```diff
@@ -878,13 +878,13 @@
   (call-to-LT 1 0 (prc-modexp-lead---ebs) 0 32))
 
 (defconstraint prc-modexp-lead---compare-ebs-and-cds (:guard (* (standing-hypothesis) (prc-hypothesis) (prc-modexp-lead-hypothesis)))
-  (call-to-LT 2 0 (+ 96 (prc-modexp-lead---ebs)) 0 (prc---cds)))
+  (call-to-LT 2 0 (+ 96 (prc-modexp-lead---bbs)) 0 (prc---cds)))
 
 (defconstraint prc-modexp-lead---compare-cds-minus-96-plus-bbs-and-32 (:guard (* (standing-hypothesis) (prc-hypothesis) (prc-modexp-lead-hypothesis)))
   (if-not-zero (prc-modexp-lead---call-data-contains-exponent-bytes)
                (call-to-LT 3
                            0
-                           (- (prc---cds) (+ 96 (prc-modexp-lead---ebs)))
+                           (- (prc---cds) (+ 96 (prc-modexp-lead---bbs)))
                            0
                            32)))
 
```
