# [?] [consensus][framework] Fix chunky DKG enable-feature: on_new_epoch + pipeline deadlock

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-03-05
Source: https://github.com/aptos-labs/aptos-core/commit/789639bec9448286f23cc31cfa2dfa232440639f
Type: security-commit

## Details
[consensus][framework] Fix chunky DKG enable-feature: on_new_epoch + pipeline deadlock

Two fixes for the enable-feature smoke test:

1. Framework: Add missing `chunky_dkg_config::on_new_epoch(framework)` call
   in `reconfiguration_with_dkg::finish()`. Without this, the chunky DKG
   config buffered via governance `set_for_next_epoch` was never applied.

2. Consensus pipeline: Break circular dependency in decryption pipeline when
   `decryption_enabled=true` but `secret_share_config=None` (bootstrapping
   epoch). The cycle was: has_rand_txns_fut -> prepare -> decrypt (waiting
   for secret_shared_key_rx from ordering) -> but ordering blocked on
   has_rand_txns_fut. Use `observer_enabled` flag to distinguish consensus
   nodes (return immediately) from observers (wait for key from leader).

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
