# [?] Update tokens list, fix USB crash on disconnect take 2, bump version

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2017-06-02
Source: https://github.com/LedgerHQ/app-ethereum/commit/37f33677c89e66d5b3d5ddac9640ab22f8a6682a
Type: security-commit

## Details
Update tokens list, fix USB crash on disconnect take 2, bump version

## Patch
### Makefile.genericwallet
```diff
@@ -25,7 +25,7 @@ APP_LOAD_PARAMS=--appFlags 0x40 --path "44'/60'" --path "44'/61'" --path "44'/1'
 
 APPVERSION_M=1
 APPVERSION_N=0
-APPVERSION_P=11
+APPVERSION_P=12
 APPVERSION=$(APPVERSION_M).$(APPVERSION_N).$(APPVERSION_P)
 
 #prepare hsm generation
```

### src_genericwallet/main.c
```diff
@@ -2520,6 +2520,9 @@ void handleApdu(volatile unsigned int *flags, volatile unsigned int *tx) {
                 break;
             }
         }
+        CATCH(EXCEPTION_IO_RESET) {
+            THROW(EXCEPTION_IO_RESET);
+        }
         CATCH_OTHER(e) {
             switch (e & 0xF000) {
             case 0x6000:
@@ -2577,6 +2580,9 @@ void sample_main(void) {
 
                 handleApdu(&flags, &tx);
             }
+            CATCH(EXCEPTION_IO_RESET) {
+                THROW(EXCEPTION_IO_RESET);
+            }
             CATCH_OTHER(e) {
                 switch (e & 0xF000) {
                 case 0x6000:
```

### src_genericwallet/tokens.c
```diff
@@ -107,6 +107,10 @@ const tokenDefinition_t const TOKENS[NUM_TOKENS] = {
       0x94, 0x73, 0xe4, 0x62, 0xc5, 0x4b, 0xae, 0x65, 0x67, 0xd9},
      "LUN ",
      18},
+    {{0xd0, 0xb1, 0x71, 0xEb, 0x0b, 0x0F, 0x2C, 0xbD, 0x35, 0xcC,
+      0xD9, 0x7c, 0xDC, 0x5E, 0xDC, 0x3f, 0xfe, 0x48, 0x71, 0xaa},
+     "MDA ",
+     18},
     {{0xe2, 0x3c, 0xd1, 0x60, 0x76, 0x1f, 0x63, 0xfc, 0x3a, 0x1c,
       0xf7, 0x8a, 0xa0, 0x34, 0xb6, 0xcd, 0xf9, 0x7d, 0x3e, 0x0c},
      "MIT ",
```

### src_genericwallet/tokens.h
```diff
@@ -23,6 +23,6 @@ typedef struct tokenDefinition_t {
     uint8_t decimals;
 } tokenDefinition_t;
 
-#define NUM_TOKENS 44 
+#define NUM_TOKENS 45
 
 extern tokenDefinition_t const TOKENS[NUM_TOKENS];
```
