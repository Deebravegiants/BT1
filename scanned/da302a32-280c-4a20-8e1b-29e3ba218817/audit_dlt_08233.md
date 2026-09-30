# [?] stakes: guard against epoch u16 overflow (slop)

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-09-01
Source: https://github.com/firedancer-io/firedancer/commit/bef15cb1a0a3b032b0f646b2144d95b99507d7e0
Type: security-commit

## Details
stakes: guard against epoch u16 overflow (slop)

add FD_CHECK_ERR that triggers in 350 years.  (useful for fuzzing
and custom clusters with shorter epochs)

## Patch
### src/flamenco/stakes/fd_stake_delegations.c
```diff
@@ -369,14 +369,6 @@ root_update( fd_stake_delegations_t * stake_delegations,
              ulong                    lamports,
              uint                     acc_dlen,
              uchar                    warmup_cooldown_rate ) {
-  /* On-chain delegation epochs are either the ULONG_MAX sentinel
-     meaning bootstrap activation or not deactivating, or near the
-     current epoch which is centuries below USHORT_MAX.  Don't allow
-     exactly USHORT_MAX as raw input epoch, because that gets
-     interpreted as the ULONG_MAX sentinel. */
-  FD_TEST( activation_epoch==ULONG_MAX   || activation_epoch<(ulong)USHORT_MAX   );
-  FD_TEST( deactivation_epoch==ULONG_MAX || deactivation_epoch<(ulong)USHORT_MAX );
-
   fd_stake_delegation_t * pool = get_root_pool( stake_delegations );
   root_map_t *            map  = get_root_map( stake_delegations );
 
@@ -393,12 +385,15 @@ root_update( fd_stake_delegations_t * stake_delegations,
     pubkey_ref_acquire( stake_delegations, stake_account );
   }
 
+  FD_CHECK_ERR( (long)activation_epoch  <USHORT_MAX, "activation_epoch overflow"   );
+  FD_CHECK_ERR( (long)deactivation_epoch<USHORT_MAX, "deactivation_epoch overflow" );
+
   stake_delegation->vote_account         = *vote_account;
   stake_delegation->stake                = stake;
   stake_delegation->lamports             = lamports;
   stake_delegation->acc_dlen             = acc_dlen;
-  stake_delegation->activation_epoch     = (ushort)fd_ulong_min( activation_epoch, USHORT_MAX );
-  stake_delegation->deactivation_epoch   = (ushort)fd_ulong_min( deactivation_epoch, USHORT_MAX );
+  stake_delegation->activation_epoch     = (ushort)activation_epoch;
+  stake_delegation->deactivation_epoch   = (ushort)deactivation_epoch;
   stake_delegation->credits_observed     = credits_observed;
   stake_delegation->warmup_cooldown_rate = warmup_cooldown_rate;
   stake_delegation->dne_in_root          = 0;
@@ -590,14 +585,6 @@ fd_stake_delegations_fork_update( fd_stake_delegations_t * stake_delegations,
                                   uchar                    warmup_cooldown_rate ) {
   fd_rwlock_write( &stake_delegations->lock );
 
-  /* On-chain delegation epochs are either the ULONG_MAX sentinel
-     meaning bootstrap activation or not deactivating, or near the
-     current epoch which is centuries below USHORT_MAX.  Don't allow
-     exactly USHORT_MAX as raw input epoch, because that gets
-     interpreted as the ULONG_MAX sentinel. */
-  FD_TEST( activation_epoch==ULONG_MAX   || activation_epoch<(ulong)USHORT_MAX   );
-  FD_TEST( deactivation_epoch==ULONG_MAX || deactivation_epoch<(ulong)USHORT_MAX );
-
   fd_stake_delegation_t * delta_pool       = get_delta_pool( stake_delegations );
   fork_map_t *            map              = get_fork_map( stake_delegations, fork_idx );
   fd_stake_delegation_t * stake_delegation = fork_map_ele_query( map, stake_account, NULL, delta_pool );
@@ -617,12 +604,14 @@ fd_stake_delegations_fork_update( fd_stake_delegations_t * stake_delegations,
   }
 
   if( FD_LIKELY( stake_delegation ) ) {
+    FD_CHECK_ERR( (long)activation_epoch  <USHORT_MAX, "activation_epoch overflow"   );
+    FD_CHECK_ERR( (long)deactivation_epoch<USHORT_MAX, "deactivation_epoch overflow" );
     stake_delegation->vote_account         = *vote_account;
     stake_delegation->stake                = stake;
     stake_delegation->lamports             = lamports;
     stake_delegation->acc_dlen             = acc_dlen;
-    stake_delegation->activation_epoch     = (ushort)fd_ulong_min( activation_epoch, USHORT_MAX );
-    stake_delegation->deactivation_epoch   = (ushort)fd_ulong_min( deactivation_epoch, USHORT_MAX );
+    stake_delegation->activation_epoch     = (ushort)activation_epoch;
+    stake_delegation->deactivation_epoch   = (ushort)deactivation_epoch;
     stake_delegation->credits_observed     = credits_observed;
     stake_delegation->warmup_cooldown_rate = warmup_cooldown_rate;
     stake_delegation->is_tombstone         = 0;
@@ -819,6 +808,8 @@ fd_stake_delegations_iter_advance_fallback( fd_stake_delegations_iter_t * iter )
       fd_delegation_t const * delegation = &stake->stake.stake.delegation;
       fd_stake_delegation_t * ele        = &iter->batch[ out ];
 
+      FD_CHECK_ERR( (long)delegation->activation_epoch  <USHORT_MAX, "activation_epoch overflow"   );
+      FD_CHECK_ERR( (long)delegation->deactivation_epoch<USHORT_MAX, "deactivation_epoch overflow" );
       ele->stake_account        = *(fd_pubkey_t const *)pubkeys[ j ];
       ele->vote_account         = delegation->voter_pubkey;
       ele->stake                = delegation->stake;
```
