# [?] Structs alignment in memory, fixes device freezes/crashes

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2022-05-05
Source: https://github.com/LedgerHQ/app-ethereum/commit/5c00a5c27bf011f3473061b8a268f2b5c1225e39
Type: security-commit

## Details
Structs alignment in memory, fixes device freezes/crashes

## Patch
### src_features/signMessageEIP712/field_hash.c
```diff
@@ -3,6 +3,7 @@
 #include "encode_field.h"
 #include "path.h"
 #include "mem.h"
+#include "mem_utils.h"
 #include "eip712.h"
 #include "shared_context.h"
 
@@ -12,7 +13,7 @@ bool field_hash_init(void)
 {
     if (fh == NULL)
     {
-        if ((fh = mem_alloc(sizeof(*fh))) == NULL)
+        if ((fh = MEM_ALLOC_AND_ALIGN_TO_TYPE(sizeof(*fh), *fh)) == NULL)
         {
             return false;
         }
@@ -36,7 +37,6 @@ bool    field_hash(const uint8_t *data,
 #endif
 
 
-    (void)data;
     if (fh == NULL)
     {
         return false;
```

### src_features/signMessageEIP712/mem_utils.c
```diff
@@ -26,10 +26,9 @@ char    *mem_alloc_and_copy_char(char c)
  * @param[in] value Value to write in memory
  * @param[out] length number of characters written to memory
  *
- * @return pointer to memory area or \ref NULL if the allocated failed
+ * @return pointer to memory area or \ref NULL if the allocation failed
  */
-char *mem_alloc_and_format_uint(uint32_t value,
-                                uint8_t *const length)
+char    *mem_alloc_and_format_uint(uint32_t value, uint8_t *const length)
 {
     char        *mem_ptr;
     uint32_t    value_copy;
@@ -55,3 +54,26 @@ char *mem_alloc_and_format_uint(uint32_t value,
     }
     return mem_ptr;
 }
+
+/**
+ * Allocate and align, required when dealing with pointers of multi-bytes data
+ * like structures that will be dereferenced at runtime.
+ *
+ * @param[in] size the size of the data we want to allocate in memory
+ * @param[in] alignment the byte alignment needed
+ *
+ * @return pointer to the memory area, \ref NULL if the allocation failed
+ */
+void    *mem_alloc_and_align(size_t size, size_t alignment)
+{
+    uint8_t align_diff = (uintptr_t)mem_alloc(0) % alignment;
+
+    if (align_diff > 0) // alignment needed
+    {
+        if (mem_alloc(alignment - align_diff) == NULL)
+        {
+            return NULL;
+        }
+    }
+    return mem_alloc(size);
+}
```

### src_features/signMessageEIP712/mem_utils.h
```diff
@@ -4,9 +4,11 @@
 #include <stdint.h>
 #include <stdbool.h>
 
+#define MEM_ALLOC_AND_ALIGN_TO_TYPE(size, type) (mem_alloc_and_align(size, __alignof__(type)))
+
 char *mem_alloc_and_copy_char(char c);
 void *mem_alloc_and_copy(const void *data, size_t size);
-char *mem_alloc_and_format_uint(uint32_t value,
-                                uint8_t *const written_chars);
+char *mem_alloc_and_format_uint(uint32_t value, uint8_t *const written_chars);
+void *mem_alloc_and_align(size_t size, size_t alignment);
 
 #endif // MEM_UTILS_H_
```

### src_features/signMessageEIP712/path.c
```diff
@@ -7,6 +7,7 @@
 #include "type_hash.h"
 #include "shared_context.h"
 #include "ethUtils.h"
+#include "mem_utils.h"
 
 static s_path *path_struct = NULL;
 
@@ -255,7 +256,7 @@ static bool path_update(void)
         const uint8_t *thash_ptr;
 
         // allocate new hash context
-        if ((hash_ctx = mem_alloc(sizeof(cx_sha3_t))) == NULL)
+        if ((hash_ctx = mem_alloc(sizeof(*hash_ctx))) == NULL)
         {
             return false;
         }
@@ -304,7 +305,7 @@ bool    path_set_root(const char *const struct_name, uint8_t name_length)
     // TODO: Move elsewhere
     cx_sha3_t *hash_ctx;
     const uint8_t *thash_ptr;
-    if ((hash_ctx = mem_alloc(sizeof(cx_sha3_t))) == NULL)
+    if ((hash_ctx = MEM_ALLOC_AND_ALIGN_TO_TYPE(sizeof(*hash_ctx), *hash_ctx)) == NULL)
     {
         return false;
     }
@@ -427,7 +428,8 @@ bool    path_new_array_depth(uint8_t size)
     }
     // TODO: Move elsewhere
     cx_sha3_t *hash_ctx;
-    if ((hash_ctx = mem_alloc(sizeof(cx_sha3_t))) == NULL)
+    // memory address not aligned, padd it
+    if ((hash_ctx = mem_alloc(sizeof(*hash_ctx))) == NULL)
     {
         return false;
     }
@@ -533,15 +535,15 @@ bool    path_advance(void)
 }
 
 /**
- * Allocates the the path indexes in memory and sets it with a depth of 0.
+ * Allocates the path indexes in memory and sets it with a depth of 0.
  *
  * @return whether the memory allocation were successful.
  */
 bool    path_init(void)
 {
     if (path_struct == NULL)
     {
-        path_struct = mem_alloc(sizeof(*path_struct));
+        path_struct = MEM_ALLOC_AND_ALIGN_TO_TYPE(sizeof(*path_struct), *path_struct);
     }
     return path_struct != NULL;
 }
```

### src_features/signMessageEIP712/type_hash.c
```diff
@@ -275,10 +275,14 @@ const uint8_t *type_hash(const void *const structs_array,
     uint8_t deps_count = 0;
     void **deps;
     uint8_t *hash_ptr;
+    void *mem_loc_bak = mem_alloc(0);
 
     cx_keccak_init(&global_sha3, 256); // init hash
     // get list of structs (own + dependencies), properly ordered
-    deps = mem_alloc(0); // get where the first elem will be
+    if ((deps = MEM_ALLOC_AND_ALIGN_TO_TYPE(0, *deps)) == NULL)
+    {
+        return NULL;
+    }
     if (get_struct_dependencies(structs_array, &deps_count, deps, struct_ptr) == false)
     {
         return NULL;
@@ -294,7 +298,7 @@ const uint8_t *type_hash(const void *const structs_array,
         encode_and_hash_type(*deps);
         deps += 1;
     }
-    mem_dealloc(sizeof(void*) * deps_count);
+    mem_dealloc(mem_alloc(0) - mem_loc_bak);
 #ifdef DEBUG
     PRINTF("\n");
 #endif
```
