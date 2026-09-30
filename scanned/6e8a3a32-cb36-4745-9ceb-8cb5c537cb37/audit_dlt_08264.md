# [?] restore: fix slot_delta_parser align/footprint to prevent oob

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-03-03
Source: https://github.com/firedancer-io/firedancer/commit/52c497cdabed92f7eda4ab3cbca37db794b47891
Type: security-commit

## Details
restore: fix slot_delta_parser align/footprint to prevent oob

## Patch
### src/discof/restore/utils/fd_slot_delta_parser.c
```diff
@@ -256,7 +256,7 @@ state_process( fd_slot_delta_parser_t * parser ) {
 
 FD_FN_CONST ulong
 fd_slot_delta_parser_align( void ) {
-  return fd_ulong_max( alignof(fd_slot_delta_parser_t), slot_set_align() );
+  return fd_ulong_max( fd_ulong_max( alignof(fd_slot_delta_parser_t), slot_pool_align() ), slot_set_align() );
 }
 
 FD_FN_CONST ulong
@@ -265,7 +265,7 @@ fd_slot_delta_parser_footprint( void ) {
   l = FD_LAYOUT_APPEND( l,  alignof(fd_slot_delta_parser_t), sizeof(fd_slot_delta_parser_t)                                  );
   l = FD_LAYOUT_APPEND( l,  slot_pool_align(),               slot_pool_footprint( FD_SLOT_DELTA_MAX_ENTRIES )                );
   l = FD_LAYOUT_APPEND( l,  slot_set_align(),                slot_set_footprint( FD_SLOT_DELTA_PARSER_SLOT_SET_MAX_ENTRIES ) );
-  return FD_LAYOUT_FINI( l, alignof(fd_slot_delta_parser_t) );
+  return FD_LAYOUT_FINI( l, fd_slot_delta_parser_align() );
 }
 
 void *
@@ -284,6 +284,7 @@ fd_slot_delta_parser_new( void * shmem ) {
   fd_slot_delta_parser_t * parser = FD_SCRATCH_ALLOC_APPEND( l, alignof(fd_slot_delta_parser_t), sizeof(fd_slot_delta_parser_t)                                  );
   void * slot_pool_mem            = FD_SCRATCH_ALLOC_APPEND( l, slot_pool_align(),               slot_pool_footprint( FD_SLOT_DELTA_MAX_ENTRIES )                );
   void * slot_set_mem             = FD_SCRATCH_ALLOC_APPEND( l, slot_set_align(),                slot_set_footprint( FD_SLOT_DELTA_PARSER_SLOT_SET_MAX_ENTRIES ) );
+  FD_TEST( FD_SCRATCH_ALLOC_FINI( l, fd_slot_delta_parser_align() ) == (ulong)shmem + fd_slot_delta_parser_footprint() );
 
   parser->slot_pool = slot_pool_join( slot_pool_new( slot_pool_mem, FD_SLOT_DELTA_MAX_ENTRIES ) );
   FD_TEST( parser->slot_pool );
```
