# [?] flamenco: fix vote lockout to return maximum in the overflow case so that votes are correctly expired

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-03-11
Source: https://github.com/firedancer-io/firedancer/commit/089080da9ab44f5a164bc0719b442acf6ff0685d
Type: security-commit

## Details
flamenco: fix vote lockout to return maximum in the overflow case so that votes are correctly expired

## Patch
### agave
```diff
@@ -1 +1 @@
-Subproject commit bcec2ca2e0218ca5470a2a5360ca520dc44898a7
+Subproject commit 49e8151a6fed417452e7f4e7eb89b6457141eec3
```

### contrib/test/test-vectors-fixtures/txn-fixtures/program-tests.list
```diff
@@ -3019,3 +3019,5 @@ dump/test-vectors/txn/fixtures/programs/5d50e47d7b6ca34bd302e53d355009252dea8f1e
 dump/test-vectors/txn/fixtures/programs/9d45f7478d50b40dd4883e5eb4970b075a5deb45_3293287.fix
 dump/test-vectors/txn/fixtures/programs/bcab39533f49cdbf55806cd02dbe81a66beaeffc_3484135.fix
 dump/test-vectors/txn/fixtures/programs/c00520e8914e5dccc9c87c106f42f742de3ec96d_3421158.fix
+dump/test-vectors/txn/fixtures/programs/4f90cc025e3d14f9757382fc753235cf96bdea8a_3551734.fix
+dump/test-vectors/txn/fixtures/programs/74ceb9783010f2045eb54a70581fb66582c7d7eb_3723552.fix
```

### src/flamenco/runtime/program/fd_vote_program.c
```diff
@@ -71,8 +71,10 @@ size_of_versioned( int is_current ) {
 // https://github.com/anza-xyz/agave/blob/v2.0.1/sdk/program/src/vote/state/mod.rs#L104
 static inline ulong
 lockout( fd_vote_lockout_t * self ) {
-  // Assumes INITIAL_LOCKOUT (the base) = 2
-  return self->confirmation_count<64U ? 1UL<<self->confirmation_count : 0UL;
+  /* Confirmation count can never be greater than MAX_LOCKOUT_HISTORY, preventing overflow.
+     Although Agave does not consider overflow, we do for fuzzing conformance. */
+  ulong confirmation_count = fd_ulong_min( self->confirmation_count, MAX_LOCKOUT_HISTORY );
+  return 1UL<<confirmation_count;
 }
 
 // https://github.com/anza-xyz/agave/blob/v2.0.1/sdk/program/src/vote/state/mod.rs#L110
```
