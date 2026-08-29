# [?] Harden secret sharing: fix panics, resolve TODOs, clean dead code (#18833)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-03-04
Source: https://github.com/aptos-labs/aptos-core/commit/1cf4d5a0bfa3702d2ded1811cee2570188d6b6f0
Type: security-commit

## Details
Harden secret sharing: fix panics, resolve TODOs, clean dead code (#18833)

* [consensus] Replace panics with proper error handling in secret sharing

Convert assert!, expect(), and unreachable!() calls to graceful error
returns in the secret sharing module. Panics in consensus code crash
validator nodes, so these should return errors instead.

- assert! → ensure! in add_self_share for author validation
- expect("Broadcast cannot fail") → warn + return in spawned task
- expect("pipeline must exist") → anyhow error propagation
- expect("Must not be None") → anyhow error propagation
- expect("Add self dec share should succeed") → ? operator
- expect("Author must exist for weight") → filter_map in retain
- expect("Author must exist in weights") → ok_or_else with anyhow
- unreachable!() in get_all_shares_authors → return None
- expect("Aggregated item should have self share") → warn + retry
- SecretShareConfig::get_id returns Result instead of panicking
- SecretShare::verify uses bounds-checked verification_keys access

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* [consensus] Resolve TODOs in secret sharing module

- Add ss_rb_config (ReliableBroadcastConfig) to ConsensusConfig for
  secret sharing, separate from rand_rb_config
- Add secret_share_request_delay_ms to ReliableBroadcastConfig with
  default of 300ms, replacing hardcoded sleep duration
- Thread config through SecretShareManager construction
- Resolve HashSet TODO in block_queue with explanatory comment

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* [consensus] Remove dead code from secret sharing types

Remove unused SecretSharingConfig struct, duplicate
FUTURE_ROUNDS_TO_ACCEPT constant, and ThresholdConfig type alias.
The actual config used is SecretShareConfig from aptos-types which

_Trimmed to 38 lines — full report: https://github.com/aptos-labs/aptos-core/commit/1cf4d5a0bfa3702d2ded1811cee2570188d6b6f0_
