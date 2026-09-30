# [?] Fix PIC crashes

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2022-05-04
Source: https://github.com/LedgerHQ/app-ethereum/commit/faae5a909c9f39199962aa7822a9517ae379b6d1
Type: security-commit

## Details
Fix PIC crashes

## Patch
### src_features/signMessageEIP712/sol_typenames.c
```diff
@@ -4,6 +4,7 @@
 #include "eip712.h"
 #include "context.h"
 #include "mem.h"
+#include "os_pic.h"
 
 // Bit indicating they are more types associated to this typename
 #define TYPENAME_MORE_TYPE  (1 << 7)
@@ -77,14 +78,14 @@ bool    init_sol_typenames(void)
                 return false;
             }
             // get pointer to the allocated space just above
-            *typename_len_ptr = strlen(typenames[s_idx]);
+            *typename_len_ptr = strlen(PIC(typenames[s_idx]));
 
             if ((typename_ptr = mem_alloc(sizeof(char) * *typename_len_ptr)) == NULL)
             {
                 return false;
             }
             // copy typename
-            memcpy(typename_ptr, typenames[s_idx], *typename_len_ptr);
+            memcpy(typename_ptr, PIC(typenames[s_idx]), *typename_len_ptr);
         }
         // increment array size
         *typenames_array += 1;
```
