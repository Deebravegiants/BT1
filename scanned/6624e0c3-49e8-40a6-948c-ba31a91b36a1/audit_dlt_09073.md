# [?] Fixes the index overflow, since header + data could be longer than 0xFF

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2022-03-21
Source: https://github.com/LedgerHQ/app-ethereum/commit/5438b39eb25c346e91095ac3737ef6b0971a0012
Type: security-commit

## Details
Fixes the index overflow, since header + data could be longer than 0xFF

## Patch
### src_features/signMessageEIP712/entrypoint.c
```diff
@@ -41,6 +41,15 @@ typedef enum
 #define INS_STRUCT_DEF  0x18
 #define INS_STRUCT_IMPL 0x1A
 
+// APDUs P1
+#define P1_COMPLETE 0x00
+#define P1_PARTIAL  0xFF
+
+// APDUs P2
+#define P2_NAME     0x00
+#define P2_ARRAY    0x0F
+#define P2_FIELD    0xFF
+
 // TypeDesc masks
 #define TYPE_MASK       (0xF)
 #define ARRAY_MASK      (1 << 7)
@@ -396,6 +405,7 @@ void    dump_mem(void)
                 {
                     case TYPE_SOL_INT:
                     case TYPE_SOL_UINT:
+                        // bytes -> bits
                         printf("%u", (byte_size * 8));
                         break;
                     case TYPE_SOL_BYTES_FIX:
@@ -446,10 +456,10 @@ bool    handle_apdu(uint8_t *data)
         case INS_STRUCT_DEF:
             switch (data[OFFSET_P2])
             {
-                case 0x00:
+                case P2_NAME:
                     set_struct_name(data);
                     break;
-                case 0xFF:
+                case P2_FIELD:
                     set_struct_field(data);
                     break;
                 default:
@@ -547,17 +557,16 @@ void    init_heap(void)
 int     main(void)
 {
     uint8_t         buf[256];
-    uint8_t         idx;
+    uint16_t        idx;
     int             state;
     uint8_t         payload_size = 0;
 
     init_heap();
 
     state = OFFSET_CLA;
     idx = 0;
-    while (true)
+    while (fread(&buf[idx], sizeof(buf[idx]), 1, stdin) > 0)
     {
-        if (fread(&buf[idx], sizeof(buf[0]), 1, stdin) == 0) break;
         switch (state)
         {
             case OFFSET_CLA:
@@ -575,7 +584,7 @@ int     main(void)
             case OFFSET_DATA:
                 if (--payload_size == 0)
                 {
-                    handle_apdu(buf);
+                    if (!handle_apdu(buf)) return false;
                     state = OFFSET_CLA;
                     idx = 0;
                 }
```
