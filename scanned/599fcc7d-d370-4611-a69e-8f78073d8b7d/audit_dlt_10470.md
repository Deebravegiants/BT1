# [?] flamenco: vote program overflow patch

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-03-05
Source: https://github.com/firedancer-io/firedancer/commit/7717e2844c70161ad80e71a119f02a576386f0fc
Type: security-commit

## Details
flamenco: vote program overflow patch

## Patch
### contrib/test/test-vectors-fixtures/instr-fixtures/vote.list
```diff
@@ -7752,3 +7752,4 @@ dump/test-vectors/instr/fixtures/vote/ffe569418052e3a00192d569f12eb7ee84f96f5c_3
 dump/test-vectors/instr/fixtures/vote/ffe9c293cfe31a6072199b47ffe9b7e56c47b924_3247128.fix
 dump/test-vectors/instr/fixtures/vote/fff5afc1cd6917cddc0f384e8c8dd393659b2a29_3157971.fix
 dump/test-vectors/instr/fixtures/vote/fff6e8387fcbd03c172a7853b2a420240a7caa0f_3157971.fix
+dump/test-vectors/instr/fixtures/vote/c986b2747f73d761f3258dbafc13f9e42863baff_1657825.fix
```

### src/flamenco/runtime/program/fd_vote_program.c
```diff
@@ -1342,9 +1342,8 @@ process_new_vote_state( fd_vote_state_t *           vote_state,
 
     // https://github.com/anza-xyz/agave/blob/v2.0.1/programs/vote/src/vote_state/mod.rs#L696
     if( FD_LIKELY( current_vote->lockout.slot < new_vote->lockout.slot ) ) {
-      ulong last_locked_out_slot =
-          current_vote->lockout.slot +
-          (ulong)pow( INITIAL_LOCKOUT, current_vote->lockout.confirmation_count );
+      ulong last_locked_out_slot = fd_ulong_sat_add( current_vote->lockout.slot,
+                                                     fd_ulong_pow2_up( current_vote->lockout.confirmation_count ) );
       // https://github.com/anza-xyz/agave/blob/v2.0.1/programs/vote/src/vote_state/mod.rs#L697
       if( last_locked_out_slot >= new_vote->lockout.slot ) {
         // https://github.com/anza-xyz/agave/blob/v2.0.1/programs/vote/src/vote_state/mod.rs#L698
```
