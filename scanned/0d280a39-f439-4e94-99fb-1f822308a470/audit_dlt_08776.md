# [?] Copy fixes to Osaka `OOB` (#794)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2025-10-13
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/565e1b376653afad58ea53efcb5874aa72c8833b
Type: security-commit

## Details
Copy fixes to Osaka `OOB` (#794)

## Patch
### oob/osaka/columns.lisp
```diff
@@ -42,7 +42,7 @@
   (ADD_FLAG :binary@prove)
   (MOD_FLAG :binary@prove)
   (BLS_REF_TABLE_FLAG :binary@prove)
-  (OUTGOING_INST :byte :display :opcode)
+  (OUTGOING_INST :i16 :display :opcode)
   (OUTGOING_DATA :i128 :array [4])
   (OUTGOING_RES_LO :i128))
 
```

### oob/osaka/constants.lisp
```diff
@@ -26,10 +26,10 @@
   CT_MAX_MODEXP_PRICING        5
   CT_MAX_MODEXP_EXTRACT        3
   CT_MAX_POINT_EVALUATION      3
-  CT_MAX_BLS_G1_ADD             3
-  CT_MAX_BLS_G1_MSM             6
-  CT_MAX_BLS_G2_ADD             3
-  CT_MAX_BLS_G2_MSM             6
+  CT_MAX_BLS_G1_ADD            3
+  CT_MAX_BLS_G1_MSM            7
+  CT_MAX_BLS_G2_ADD            3
+  CT_MAX_BLS_G2_MSM            7
   CT_MAX_BLS_PAIRING_CHECK     4
   CT_MAX_BLS_MAP_FP_TO_G1      3
   CT_MAX_BLS_MAP_FP2_TO_G2     3
```

### oob/osaka/lookups/oob-into-add.lisp
```diff
@@ -2,7 +2,7 @@
   oob.ADD_FLAG)
 
 (defclookup
-  oob-into-add
+  (oob-into-add :unchecked)
   ;; target columns
   (
     add.ARG_1
```

### oob/osaka/lookups/oob-into-mod.lisp
```diff
@@ -2,7 +2,7 @@
   oob.MOD_FLAG)
 
 (defclookup
-  oob-into-mod
+  (oob-into-mod :unchecked)
   ;; target columns
   (
     mod.ARG_1_HI
```
