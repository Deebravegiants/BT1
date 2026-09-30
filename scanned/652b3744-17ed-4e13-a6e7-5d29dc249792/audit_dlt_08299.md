# [?] flamenco: vote program overflow patch

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-03-05
Source: https://github.com/firedancer-io/firedancer/commit/97c08c390c7888ef4d0f7761a1538ee6bd75b772
Type: security-commit

## Details
flamenco: vote program overflow patch

## Patch
### contrib/test/test-vectors-fixtures/txn-fixtures/program-tests.list
```diff
@@ -3009,4 +3009,7 @@ dump/test-vectors/txn/fixtures/programs/e42ae069b62626e3de8109e8dc4809551e68bd34
 dump/test-vectors/txn/fixtures/programs/e8e647c255e74eadb162a0d4912753163cca983d_825646.fix
 dump/test-vectors/txn/fixtures/programs/ead9a360b9fe6cbbb5cb355b93fab0688aecbdf2_2371838.fix
 dump/test-vectors/txn/fixtures/programs/f4c0c1e5d6c427188f8158a077f8cf2a61ec47e8_1576433.fix
-dump/test-vectors/txn/fixtures/programs/f9ddcabf1339d1863b76341e2a2a5a7bea577ca0_1576134.fix
\ No newline at end of file
+dump/test-vectors/txn/fixtures/programs/f9ddcabf1339d1863b76341e2a2a5a7bea577ca0_1576134.fix
+dump/test-vectors/txn/fixtures/programs/5d50e47d7b6ca34bd302e53d355009252dea8f1e_2080038.fix
+dump/test-vectors/txn/fixtures/programs/9d45f7478d50b40dd4883e5eb4970b075a5deb45_2042655.fix
+dump/test-vectors/txn/fixtures/programs/c00520e8914e5dccc9c87c106f42f742de3ec96d_2117728.fix
```

### src/flamenco/runtime/program/fd_vote_program.c
```diff
@@ -1342,8 +1342,13 @@ process_new_vote_state( fd_vote_state_t *           vote_state,
 
     // https://github.com/anza-xyz/agave/blob/v2.0.1/programs/vote/src/vote_state/mod.rs#L696
     if( FD_LIKELY( current_vote->lockout.slot < new_vote->lockout.slot ) ) {
+      /* The agave implementation of calculating the last locked out
+         slot does not calculate a min between the current vote's
+         confirmation count and max lockout history. The reason we do
+         this is to make sure that the fuzzers continue working:
+         the max lockout history can not be > MAX_LOCKOUT_HISTORY. */
       ulong last_locked_out_slot = fd_ulong_sat_add( current_vote->lockout.slot,
-                                                     fd_ulong_pow2_up( current_vote->lockout.confirmation_count ) );
+                                                     fd_ulong_pow2_up( fd_ulong_min( current_vote->lockout.confirmation_count, MAX_LOCKOUT_HISTORY ) ) );
       // https://github.com/anza-xyz/agave/blob/v2.0.1/programs/vote/src/vote_state/mod.rs#L697
       if( last_locked_out_slot >= new_vote->lockout.slot ) {
         // https://github.com/anza-xyz/agave/blob/v2.0.1/programs/vote/src/vote_state/mod.rs#L698
```
