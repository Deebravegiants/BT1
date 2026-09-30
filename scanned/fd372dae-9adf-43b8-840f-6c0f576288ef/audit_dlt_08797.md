# [?] fix(oob): debug constraints (#219)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2024-05-31
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/a1ac0f42c6cfbf15f24a3410854c20d355920c1e
Type: security-commit

## Details
fix(oob): debug constraints (#219)

## Patch
### Makefile
```diff
@@ -118,13 +118,13 @@ ZKEVM_MODULES := ${ALU} \
 		 ${TABLES} \
 		 ${TRM} \
 		 ${TXN_DATA} \
+         ${OOB} \
 		 ${WCP}
 
 # TODO: add later
 #        ${GAS} \
 #		 ${HUB} \
          ${EXP} \
-         ${OOB} \
 
 define.go: ${ZKEVM_MODULES}
 	${CORSET} wizard-iop -vv -P define -o $@ ${ZKEVM_MODULES}
```

### oob/constraints.lisp
```diff
@@ -630,11 +630,11 @@
   (callToISZERO 2 0 (create___nonce)))
 
 (defconstraint justify-hub-predictions-create (:guard (* (standing-hypothesis) (create-hypothesis)))
-  (begin (eq! (call___aborting_condition)
+  (begin (eq! (create___aborting_condition)
               (+ (create___insufficient_balance_abort)
                  (* (- 1 (create___insufficient_balance_abort)) (create___stack_depth_abort))))
          (eq! (create___failure_condition)
-              (+ (- 1 (create___aborting_condition))
+              (* (- 1 (create___aborting_condition))
                  (+ (create___has_code)
                     (* (- 1 (create___has_code)) (create___nonzero_nonce)))))))
 
```
