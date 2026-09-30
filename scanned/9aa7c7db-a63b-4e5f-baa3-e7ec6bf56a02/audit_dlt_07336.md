# [?] fix(oob): oob inst modexp lead (#300)

## Summary
Severity: Unknown
Chain: Linea
Component: Consensys/linea-monorepo
Published: 2024-08-22
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/4c842637167821c75bf8632653511a3f2c340a0b
Type: security-commit

## Details
fix(oob): oob inst modexp lead (#300)

Signed-off-by: Francois Bojarski <francois.bojarski@consensys.net>
Co-authored-by: François Bojarski <54240434+letypequividelespoubelles@users.noreply.github.com>
Co-authored-by: Francois Bojarski <francois.bojarski@consensys.net>

## Patch
### Makefile
```diff
@@ -1,7 +1,8 @@
 CORSET ?= corset
 
- HUB :=  $(wildcard hub/columns/*lisp) \
- 	$(wildcard hub/constraints/account-rows/*lisp) \
+ HUB :=  $(wildcard hub/columns/*lisp)
+
+ #	$(wildcard hub/constraints/account-rows/*lisp) \
  	$(wildcard hub/constraints/context-rows/*lisp) \
  	$(wildcard hub/constraints/generalities/*lisp) \
  	$(wildcard hub/constraints/heartbeat/*lisp) \
@@ -117,6 +118,7 @@ ZKEVM_MODULES := ${ALU} \
 		 ${EUC} \
 		 ${EXP} \
 		 ${GAS} \
+ 		 ${HUB} \
 		 ${LIBRARY} \
 		 ${LOG_DATA} \
 		 ${LOG_INFO} \
@@ -136,7 +138,6 @@ ZKEVM_MODULES := ${ALU} \
 		 ${TXN_DATA} \
 		 ${WCP}
 
-# 		 ${HUB} \
 #		 ${STP} \
 
 
```

### oob/constraints.lisp
```diff
@@ -955,11 +955,12 @@
   (callToLT 2 0 (+ 96 (prc-modexp-lead---ebs)) 0 (prc---cds)))
 
 (defconstraint valid-prc-modexp-lead-future-future-future (:guard (* (standing-hypothesis) (prc-hypothesis) (prc-modexp-lead-hypothesis)))
-  (callToLT 3
-            0
-            (- (prc---cds) (+ 96 (prc-modexp-lead---ebs)))
-            0
-            32))
+  (if-not-zero (prc-modexp-lead---call-data-contains-exponent-bytes)
+               (callToLT 3
+                         0
+                         (- (prc---cds) (+ 96 (prc-modexp-lead---ebs)))
+                         0
+                         32)))
 
 (defconstraint justify-hub-predictions-prc-modexp-lead (:guard (* (standing-hypothesis) (prc-hypothesis) (prc-modexp-lead-hypothesis)))
   (begin (eq! (prc-modexp-lead---load-lead)
```
