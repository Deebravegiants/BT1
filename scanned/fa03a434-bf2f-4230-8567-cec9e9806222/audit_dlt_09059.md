# [?] Fixed crash in free when given NULL

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-02-02
Source: https://github.com/LedgerHQ/app-ethereum/commit/afb97b7dec5c6e1aecde05123cb32a6fcbd84264
Type: security-commit

## Details
Fixed crash in free when given NULL

## Patch
### src/mem.c
```diff
@@ -49,11 +49,13 @@ void *app_mem_alloc_impl(size_t size, bool persistent, const char *file, int lin
 }
 
 void app_mem_free_impl(void *ptr, const char *file, int line) {
+    if (ptr != NULL) {
 #ifdef HAVE_MEMORY_PROFILING
-    PRINTF(MP_LOG_PREFIX "free;0x%p;%s:%u\n", ptr, file, line);
+        PRINTF(MP_LOG_PREFIX "free;0x%p;%s:%u\n", ptr, file, line);
 #else
-    (void) file;
-    (void) line;
+        (void) file;
+        (void) line;
 #endif
-    mem_free(mem_ctx, ptr);
+        mem_free(mem_ctx, ptr);
+    }
 }
```
