# [?] runtime: fix solfuzz failure crash

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-09-11
Source: https://github.com/firedancer-io/firedancer/commit/873c1fc4a141a399d47775c60c1f67493854e162
Type: security-commit

## Details
runtime: fix solfuzz failure crash

Instruction context lifecycle managed is not correctly designed.
If an execution failure occurs during context setup, a partially
initialized object gets generated.  When destroying this object,
null pointer dereferences etc occur.

Additionally, "funk handholding" checks are just entirely broken
and result in the opposite of what they are supposed to achieve:
Enabling 'handholding' silently *hides* bugs from the user instead
of revealing them.

This patch is not a full fix but fixes some smaller issues:

- funk: crash if txn_prepare or txn_cancel is called with obviously
  invalid inputs (instead of only crashing if handholding is NOT
  enabled)

- solfuzz: crash instead of silently failing (and segfaulting) for
  various alloc failure cases in the instruction fuzzer

- solfuzz: fix null-pointer-deref if instruction fuzz context fails
  to bootstrap early (NULL txn provided to funk_txn_cancel)

## Patch
### src/flamenco/runtime/tests/fd_instr_harness.c
```diff
@@ -35,6 +35,7 @@ fd_runtime_fuzz_instr_ctx_create( fd_solfuzz_runner_t *                runner,
 
   fd_funk_txn_start_write( funk );
   fd_funk_txn_t * funk_txn = fd_funk_txn_prepare( funk, NULL, xid, 1 );
+  if( FD_UNLIKELY( !funk_txn ) ) FD_LOG_ERR(( "fd_funk_txn_prepare failed" ));
   fd_funk_txn_end_write( funk );
 
   /* Allocate contexts */
@@ -66,23 +67,15 @@ fd_runtime_fuzz_instr_ctx_create( fd_solfuzz_runner_t *                runner,
 
   /* Setup vote states accounts */
   fd_vote_states_t * vote_states = fd_vote_states_join( fd_vote_states_new( fd_bank_vote_states_locking_modify( slot_ctx->bank ), FD_RUNTIME_MAX_VOTE_ACCOUNTS, 999UL ) );
-  if( FD_UNLIKELY( !vote_states ) ) {
-    return 0;
-  }
+  if( FD_UNLIKELY( !vote_states ) ) FD_LOG_ERR(( "fd_vote_states_new failed" ));
   fd_bank_vote_states_end_locking_modify( slot_ctx->bank );
 
   fd_vote_states_t * vote_states_prev = fd_vote_states_join( fd_vote_states_new( fd_bank_vote_states_prev_locking_modify( slot_ctx->bank ), FD_RUNTIME_MAX_VOTE_ACCOUNTS, 999UL ) );
-  if( FD_UNLIKELY( !vote_states_prev ) ) {
-    fd_bank_vote_states_prev_end_locking_modify( slot_ctx->bank );
-    return 0;
-  }
+  if( FD_UNLIKELY( !vote_states_prev ) ) FD_LOG_ERR(( "fd_vote_states_new for prev failed" ));
   fd_bank_vote_states_prev_end_locking_modify( slot_ctx->bank );
 
   fd_vote_states_t * vote_states_prev_prev = fd_vote_states_join( fd_vote_states_new( fd_bank_vote_states_prev_prev_locking_modify( slot_ctx->bank ), FD_RUNTIME_MAX_VOTE_ACCOUNTS, 999UL ) );
-  if( FD_UNLIKELY( !vote_states_prev_prev ) ) {
-    fd_bank_vote_states_prev_prev_end_locking_modify( slot_ctx->bank );
-    return 0;
-  }
+  if( FD_UNLIKELY( !vote_states_prev_prev ) ) FD_LOG_ERR(( "fd_vote_staets_new for prev2 failed" ));
   fd_bank_vote_states_prev_prev_end_locking_modify( slot_ctx->bank );
 
   /* Set up epoch context. Defaults obtained from GenesisConfig::Default() */
@@ -410,9 +403,7 @@ void
 fd_runtime_fuzz_instr_ctx_destroy( fd_solfuzz_runner_t * runner,
                                    fd_exec_instr_ctx_t * ctx ) {
   if( !ctx ) return;
-  fd_funk_txn_t * funk_txn = ctx->txn_ctx->funk_txn;
-
-  fd_funk_txn_cancel( runner->funk, funk_txn, 1 );
+  fd_funk_txn_cancel_all( runner->funk, 1 );
 }
 
 
```

### src/funk/fd_funk_txn.c
```diff
@@ -51,23 +51,15 @@ fd_funk_txn_prepare( fd_funk_t *               funk,
                      fd_funk_txn_xid_t const * xid,
                      int                       verbose ) {
 
+  if( FD_UNLIKELY( !funk ) ) FD_LOG_CRIT(( "NULL funk" ));
+  if( FD_UNLIKELY( !xid  ) ) FD_LOG_CRIT(( "NULL xid"  ));
+  if( FD_UNLIKELY( fd_funk_txn_xid_eq_root( xid ) ) ) FD_LOG_CRIT(( "xid is root" ));
+
 #ifdef FD_FUNK_HANDHOLDING
-  if( FD_UNLIKELY( !funk ) ) {
-    if( FD_UNLIKELY( verbose ) ) FD_LOG_WARNING(( "NULL funk" ));
-    return NULL;
-  }
-  if( FD_UNLIKELY( !xid ) ) {
-    if( FD_UNLIKELY( verbose ) ) FD_LOG_WARNING(( "NULL xid" ));
-    return NULL;
-  }
   if( FD_UNLIKELY( parent && !fd_funk_txn_valid( funk, parent ) ) ) {
     if( FD_UNLIKELY( verbose ) ) FD_LOG_WARNING(( "bad txn" ));
     return NULL;
   }
-  if( FD_UNLIKELY( fd_funk_txn_xid_eq_root( xid ) ) ) {
-    if( FD_UNLIKELY( verbose ) ) FD_LOG_WARNING(( "xid is the root" ));
-    return NULL;
-  }
   if( FD_UNLIKELY( fd_funk_txn_xid_eq( xid, funk->shmem->last_publish ) ) ) {
     if( FD_UNLIKELY( verbose ) ) FD_LOG_WARNING(( "xid is the last published" ));
     return NULL;
@@ -273,11 +265,9 @@ fd_funk_txn_cancel( fd_funk_t *     funk,
                     fd_funk_txn_t * txn,
                     int             verbose ) {
 
+  if( FD_UNLIKELY( !funk ) ) FD_LOG_CRIT(( "NULL funk" ));
+  if( FD_UNLIKELY( !txn  ) ) FD_LOG_CRIT(( "NULL txn"  ));
 #ifdef FD_FUNK_HANDHOLDING
-  if( FD_UNLIKELY( !funk ) ) {
-    if( FD_UNLIKELY( verbose ) ) FD_LOG_WARNING(( "NULL funk" ));
-    return 0UL;
-  }
   if( FD_UNLIKELY( !fd_funk_txn_valid( funk, txn ) ) ) {
     if( FD_UNLIKELY( verbose ) ) FD_LOG_WARNING(( "bad txn" ));
     return 0UL;
```

### src/funk/test_funk_txn.c
```diff
@@ -191,9 +191,7 @@ main( int     argc,
       uint idx; RANDOM_SET_BIT_IDX( ~live_pmap );
       fd_funk_txn_t * txn = fd_funk_txn_query( &recent_xid[idx], map );
       FD_TEST( !txn );
-#ifdef FD_FUNK_HANDHOLDING
-      FD_TEST( fd_funk_txn_cancel( funk, txn, verbose )==0UL );
-#endif
+      // FD_TEST( fd_funk_txn_cancel( funk, txn, verbose )==0UL );
       break;
     }
 
@@ -202,9 +200,7 @@ main( int     argc,
       xid[0] = fd_funk_generate_xid();
       fd_funk_txn_t * txn = fd_funk_txn_query( xid, map );
       FD_TEST( !txn );
-#ifdef FD_FUNK_HANDHOLDING
-      FD_TEST( fd_funk_txn_cancel( funk, txn, verbose )==0UL );
-#endif
+      // FD_TEST( fd_funk_txn_cancel( funk, txn, verbose )==0UL );
       break;
     }
 
@@ -255,14 +251,14 @@ main( int     argc,
       /* Too many in-prep already tested */
       /* Live xid cases already tested */
 
-      FD_TEST( !fd_funk_txn_prepare( NULL, txn, xid,             verbose ) ); /* NULL funk */
-      FD_TEST( !fd_funk_txn_prepare( funk, txn, NULL,            verbose ) ); /* NULL xid */
-      FD_TEST( !fd_funk_txn_prepare( funk, txn, last_publish,    verbose ) ); /* last published xid */
+      // FD_TEST( !fd_funk_txn_prepare( NULL, txn, xid,             verbose ) ); /* NULL funk */
+      // FD_TEST( !fd_funk_txn_prepare( funk, txn, NULL,            verbose ) ); /* NULL xid */
+      // FD_TEST( !fd_funk_txn_prepare( funk, txn, last_publish,    verbose ) ); /* last published xid */
       FD_TEST( !fd_funk_txn_prepare( funk, bad, xid,             verbose ) ); /* Parent not in map */
       if( dead ) FD_TEST( !fd_funk_txn_prepare( funk, dead, xid, verbose ) ); /* Parent not in prep */
 
-      FD_TEST( !fd_funk_txn_cancel( NULL, txn,  verbose ) );                  /* NULL funk (and maybe NULL txn) */
-      FD_TEST( !fd_funk_txn_cancel( funk, NULL, verbose ) );                  /* NULL txn */
+      // FD_TEST( !fd_funk_txn_cancel( NULL, txn,  verbose ) );                  /* NULL funk (and maybe NULL txn) */
+      // FD_TEST( !fd_funk_txn_cancel( funk, NULL, verbose ) );                  /* NULL txn */
       FD_TEST( !fd_funk_txn_cancel( funk, bad,  verbose ) );                  /* tx not in map */
       if( dead ) FD_TEST( !fd_funk_txn_cancel( funk, dead, verbose ) );       /* tx not in prep */
 
```
