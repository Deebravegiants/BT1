# [?] bank: potential double free

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-11-03
Source: https://github.com/firedancer-io/firedancer/commit/7f2631e5e7d2601f1e26fd88894c33ca589c8ede
Type: security-commit

## Details
bank: potential double free

## Patch
### src/flamenco/runtime/fd_bank.c
```diff
@@ -797,12 +797,12 @@ fd_banks_advance_root( fd_banks_t * banks,
     /* Decide if we need to free any CoW fields. We free a CoW member
        from its pool if the dirty flag is set unless it is the same
        pool that the new root uses. */
-    #define HAS_COW_1(name)                                                          \
-      if( head->name##_dirty && head->name##_pool_idx!=new_root->name##_pool_idx ) { \
-        fd_rwlock_write( &banks->name##_pool_lock );                                 \
-        fd_bank_##name##_t * name##_pool = fd_banks_get_##name##_pool( banks );      \
-        fd_bank_##name##_pool_idx_release( name##_pool, head->name##_pool_idx );     \
-        fd_rwlock_unwrite( &banks->name##_pool_lock );                               \
+    #define HAS_COW_1(name)                                                                                                  \
+      if( head->name##_dirty && head->name##_pool_idx!=new_root->name##_pool_idx && head->flags&FD_BANK_FLAGS_REPLAYABLE ) { \
+        fd_rwlock_write( &banks->name##_pool_lock );                                                                         \
+        fd_bank_##name##_t * name##_pool = fd_banks_get_##name##_pool( banks );                                              \
+        fd_bank_##name##_pool_idx_release( name##_pool, head->name##_pool_idx );                                             \
+        fd_rwlock_unwrite( &banks->name##_pool_lock );                                                                       \
       }
     /* Do nothing for these. */
     #define HAS_COW_0(name)
```
