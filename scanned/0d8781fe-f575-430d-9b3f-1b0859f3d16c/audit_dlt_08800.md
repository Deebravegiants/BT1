# [?] fix(ecdata and oob): constants naming and visibility (#179)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2024-05-16
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/b60e96d390b88939d6d5b79e49f2d1b31d41c759
Type: security-commit

## Details
fix(ecdata and oob): constants naming and visibility (#179)

Resolves: #178 

Signed-off-by: Lorenzo Gentile <lorenzo.gentile@consensys.net>

## Patch
### constants/constants.lisp
```diff
@@ -283,14 +283,14 @@
   ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; EC DATA MODULE ;;
   ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;                ;;
   ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
-  EC_DATA_PHASE_ECRECOVER_DATA           1
-  EC_DATA_PHASE_ECRECOVER_RESULT         2
-  EC_DATA_PHASE_ECADD_DATA               3
-  EC_DATA_PHASE_ECADD_RESULT             4
-  EC_DATA_PHASE_ECMUL_DATA               5
-  EC_DATA_PHASE_ECMUL_RESULT             6
-  EC_DATA_PHASE_PAIRING_DATA             7
-  EC_DATA_PHASE_PAIRING_RESULT           8
+  PHASE_ECRECOVER_DATA          0x010A
+  PHASE_ECRECOVER_RESULT        0x010B
+  PHASE_ECADD_DATA              0x060A
+  PHASE_ECADD_RESULT            0x060B
+  PHASE_ECMUL_DATA              0x070A
+  PHASE_ECMUL_RESULT            0x070B
+  PHASE_ECPAIRING_DATA          0x080A
+  PHASE_ECPAIRING_RESULT        0x080B
   ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
   ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;            ;;
   ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; EXP MODULE ;;
@@ -356,29 +356,29 @@
   ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; OOB MODULE ;;
   ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;            ;;
   ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
-  OOB_INST_jump                          0x56
-  OOB_INST_jumpi                         0x57
-  OOB_INST_rdc                           0x3E
-  OOB_INST_cdl                           0x35
-  OOB_INST_xcall                         0xCC
-  OOB_INST_call                          0xCA
-  OOB_INST_create                        0xCE
-  OOB_INST_sstore                        0x55
-  OOB_INST_deployment                    0xF3
-  OOB_INST_ecrecover                     0xFF01
-  OOB_INST_sha2                          0xFF02
-  OOB_INST_ripemd                        0xFF03
-  OOB_INST_identity                      0xFF04
-  OOB_INST_ecadd                         0xFF06
-  OOB_INST_ecmul                         0xFF07
-  OOB_INST_ecpairing                     0xFF08
-  OOB_INST_blake_cds                     0xFA09
-  OOB_INST_blake_params                  0xFB09
-  OOB_INST_modexp_cds                    0xFA05
-  OOB_INST_modexp_xbs                    0xFB05
-  OOB_INST_modexp_lead                   0xFC05
-  OOB_INST_modexp_pricing                0xFD05
-  OOB_INST_modexp_extract                0xFE05
+  OOB_INST_JUMP                          0x56
+  OOB_INST_JUMPI                         0x57
+  OOB_INST_RDC                           0x3E
+  OOB_INST_CDL                           0x35
+  OOB_INST_XCALL                         0xCC
+  OOB_INST_CALL                          0xCA
+  OOB_INST_CREATE                        0xCE
+  OOB_INST_SSTORE                        0x55
+  OOB_INST_DEPLOYMENT                    0xF3
+  OOB_INST_ECRECOVER                     0xFF01
+  OOB_INST_SHA2                          0xFF02
+  OOB_INST_RIPEMD                        0xFF03
+  OOB_INST_IDENTITY                      0xFF04
+  OOB_INST_ECADD                         0xFF06
+  OOB_INST_ECMUL                         0xFF07
+  OOB_INST_ECPAIRING                     0xFF08
+  OOB_INST_BLAKE_CDS                     0xFA09
+  OOB_INST_BLAKE_PARAMS                  0xFB09
+  OOB_INST_MODEXP_CDS                    0xFA05
+  OOB_INST_MODEXP_XBS                    0xFB05
+  OOB_INST_MODEXP_LEAD                   0xFC05
+  OOB_INST_MODEXP_PRICING                0xFD05
+  OOB_INST_MODEXP_EXTRACT                0xFE05
   ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
   ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;             ;;
   ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; RLP* MODULE ;;
```

### ecdata/constants.lisp
```diff
@@ -5,22 +5,12 @@
   P_BN_LO                       0x97816a916871ca8d3c208c16d87cfd47
   SECP256K1N_HI                 0xffffffffffffffffffffffffffffffff
   SECP256K1N_LO                 0xfffffffffffffffffffffffefffffc2f
-  LT                            0x10
-  EQ                            0x14
   MULMOD                        0x09
   ADDMOD                        0x08
   ECRECOVER                     0x01
   ECADD                         0x06
   ECMUL                         0x07
   ECPAIRING                     0x08
-  PHASE_ECRECOVER_DATA          0x010A
-  PHASE_ECRECOVER_RESULT        0x010B
-  PHASE_ECADD_DATA              0x060A
-  PHASE_ECADD_RESULT            0x060B
-  PHASE_ECMUL_DATA              0x070A
-  PHASE_ECMUL_RESULT            0x070B
-  PHASE_ECPAIRING_DATA          0x080A
-  PHASE_ECPAIRING_RESULT        0x080B
   INDEX_MAX_ECRECOVER_DATA      7
   INDEX_MAX_ECADD_DATA          7
   INDEX_MAX_ECMUL_DATA          5
```

### ecdata/constraints.lisp
```diff
@@ -382,23 +382,23 @@
 ;;;;;;;;;;;;;;;;;;;;;;;;;
 (defun (callToLT k a b c d)
   (begin (eq! (shift WCP_FLAG k) 1)
-         (eq! (shift WCP_INST k) LT)
+         (eq! (shift WCP_INST k) EVM_INST_LT)
          (eq! (shift WCP_ARG1_HI k) a)
          (eq! (shift WCP_ARG1_LO k) b)
          (eq! (shift WCP_ARG2_HI k) c)
          (eq! (shift WCP_ARG2_LO k) d)))
 
 (defun (callToEQ k a b c d)
   (begin (eq! (shift WCP_FLAG k) 1)
-         (eq! (shift WCP_INST k) EQ)
+         (eq! (shift WCP_INST k) EVM_INST_EQ)
          (eq! (shift WCP_ARG1_HI k) a)
          (eq! (shift WCP_ARG1_LO k) b)
          (eq! (shift WCP_ARG2_HI k) c)
          (eq! (shift WCP_ARG2_LO k) d)))
 
 (defun (callToISZERO k a b)
   (begin (eq! (shift WCP_FLAG k) 1)
-         (eq! (shift WCP_INST k) ISZERO)
+         (eq! (shift WCP_INST k) EVM_INST_ISZERO)
          (eq! (shift WCP_ARG1_HI k) a)
          (eq! (shift WCP_ARG1_LO k) b)
          (debug (vanishes! (shift WCP_ARG2_HI k)))
```

### hub/constraints/miscellaneous-rows/oob.lisp
```diff
@@ -13,7 +13,7 @@
          pc_new_lo           ;; low  part of proposed new program counter
          code_size           ;; code size of byte code currently executing
          ) (begin
-         (eq! (shift misc/OOB_INST             kappa) OOB_INST_jump )
+         (eq! (shift misc/OOB_INST             kappa) OOB_INST_JUMP )
          (eq! (shift [ misc/OOB_DATA 1 ]       kappa) pc_new_hi)
          (eq! (shift [ misc/OOB_DATA 2 ]       kappa) pc_new_lo)
          ;; (eq! (shift [ misc/OOB_DATA 3 ]    kappa) )
@@ -32,7 +32,7 @@
          jump_condition_lo   ;; low  part of jump condition
          code_size           ;; code size of byte code currently executing
          ) (begin
-         (eq! (shift misc/OOB_INST             kappa) OOB_INST_jumpi)
+         (eq! (shift misc/OOB_INST             kappa) OOB_INST_JUMPI)
          (eq! (shift [ misc/OOB_DATA 1 ]       kappa) pc_new_hi)
          (eq! (shift [ misc/OOB_DATA 2 ]       kappa) pc_new_lo)
          (eq! (shift [ misc/OOB_DATA 3 ]       kappa) jump_condition_hi)
@@ -47,7 +47,7 @@
          kappa               ;; offset
          gas_actual          ;; GAS_ACTUAL
          ) (begin
-         (eq! (shift misc/OOB_INST          kappa) OOB_INST_sstore )
+         (eq! (shift misc/OOB_INST          kappa) OOB_INST_SSTORE )
          ;; (eq! (shift [ misc/OOB_DATA 1 ]    kappa) )
          ;; (eq! (shift [ misc/OOB_DATA 2 ]    kappa) )
          ;; (eq! (shift [ misc/OOB_DATA 3 ]    kappa) )
@@ -64,7 +64,7 @@
          offset_lo           ;; offset within call data, low  part
          call_data_size      ;; call data size
          ) (begin
-         (eq! (shift misc/OOB_INST          kappa) OOB_INST_cdl )
+         (eq! (shift misc/OOB_INST          kappa) OOB_INST_CDL )
          (eq! (shift [ misc/OOB_DATA 1 ]    kappa) offset_hi)
          (eq! (shift [ misc/OOB_DATA 2 ]    kappa) offset_lo)
          ;; (eq! (shift [ misc/OOB_DATA 3 ]    kappa) )
@@ -83,7 +83,7 @@
          size_lo                 ;; size of data to copy, low  part
          return_data_size        ;; return data size
          ) (begin
-         (eq! (shift misc/OOB_INST          kappa) OOB_INST_rdc)
+         (eq! (shift misc/OOB_INST          kappa) OOB_INST_RDC)
          (eq! (shift [ misc/OOB_DATA 1 ]    kappa) source_offset_hi)
          (eq! (shift [ misc/OOB_DATA 2 ]    kappa) source_offset_lo)
          (eq! (shift [ misc/OOB_DATA 3 ]    kappa) size_hi)
@@ -99,7 +99,7 @@
          code_size_hi                     ;; code size hi
          code_size_lo                     ;; code size lo
          ) (begin
-         (eq! (shift misc/OOB_INST          kappa)   OOB_INST_deployment )
+         (eq! (shift misc/OOB_INST          kappa)   OOB_INST_DEPLOYMENT )
          (eq! (shift [ misc/OOB_DATA 1 ]    kappa)   code_size_hi)
          (eq! (shift [ misc/OOB_DATA 2 ]    kappa)   code_size_lo)
          ;; (eq! (shift [ misc/OOB_DATA 3 ]    kappa) )
@@ -116,7 +116,7 @@
          value_hi        ;; value (high part)
          value_lo        ;; value (low  part, stack argument of CALL-type instruction)
          ) (begin
-         (eq!    (shift misc/OOB_INST          kappa)   OOB_INST_xcall )
+         (eq!    (shift misc/OOB_INST          kappa)   OOB_INST_XCALL )
          (eq!    (shift [ misc/OOB_DATA 1 ]    kappa)   value_hi       )
          (eq!    (shift [ misc/OOB_DATA 2 ]    kappa)   value_lo       )
          ;; (eq!    (shift [ misc/OOB_DATA 3 ]    kappa) )
@@ -135,7 +135,7 @@
          balance            ;; balance (from caller account)
          call_stack_depth   ;; call stack depth
          ) (begin
-         (eq!    (shift misc/OOB_INST          kappa)   OOB_INST_call   )
+         (eq!    (shift misc/OOB_INST          kappa)   OOB_INST_CALL   )
          (eq!    (shift [ misc/OOB_DATA 1 ]    kappa)   value_hi        )
          (eq!    (shift [ misc/OOB_DATA 2 ]    kappa)   value_lo        )
          (eq!    (shift [ misc/OOB_DATA 3 ]    kappa)   balance         )
@@ -156,7 +156,7 @@
          has_code           ;; callee's HAS_CODE
          call_stack_depth   ;; current call stack depth
          ) (begin
-         (eq!    (shift misc/OOB_INST          kappa)   OOB_INST_create  )
+         (eq!    (shift misc/OOB_INST          kappa)   OOB_INST_CREATE  )
          (eq!    (shift [ misc/OOB_DATA 1 ]    kappa)   value_hi         )
          (eq!    (shift [ misc/OOB_DATA 2 ]    kappa)   value_lo         )
          (eq!    (shift [ misc/OOB_DATA 3 ]    kappa)   balance          )
```

### oob/constants.lisp
```diff
@@ -17,21 +17,12 @@
   CT_MAX_ECADD            2
   CT_MAX_ECMUL            2
   CT_MAX_ECPAIRING        4
-  CT_MAX_BLAKE2F_cds      1
-  CT_MAX_BLAKE2F_params   1
-  CT_MAX_MODEXP_cds       2
-  CT_MAX_MODEXP_xbs       2
-  CT_MAX_MODEXP_lead      3
-  CT_MAX_MODEXP_pricing   5
-  CT_MAX_MODEXP_extract   3
-  LT                      0x10    ;; TODO: remove and replace by EVM_INST_XXX
-  ISZERO                  0x15
-  ADD                     0x01
-  DIV                     0x04
-  MOD                     0x06
-  GT                      0x11
-  EQ                      0x14
-  G_CALLSTIPEND           2300   ;; TODO: remove and replace by GAS_CONST_G_XXX
-  G_QUADDIVISOR           3)
+  CT_MAX_BLAKE2F_CDS      1
+  CT_MAX_BLAKE2F_PARAMS   1
+  CT_MAX_MODEXP_CDS       2
+  CT_MAX_MODEXP_XBS       2
+  CT_MAX_MODEXP_LEAD      3
+  CT_MAX_MODEXP_PRICING   5
+  CT_MAX_MODEXP_EXTRACT   3)
 
 
```
