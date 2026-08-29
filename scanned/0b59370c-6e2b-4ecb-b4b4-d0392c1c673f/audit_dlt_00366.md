# [?] [consensus] Harden SecretShare ingress validation against DoS (#19475)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-04-18
Source: https://github.com/aptos-labs/aptos-core/commit/b4ca925a9e657868dc6a1cceaeef3c70c036e6b1
Type: security-commit

## Details
[consensus] Harden SecretShare ingress validation against DoS (#19475)

* [crypto] Make weighted config player lookups fallible

Return Result instead of panicking on out-of-bounds player ids in
get_virtual_player, get_player_weight, and get_all_virtual_players.
Callers that operate on remotely-authored input (e.g. PVSS verify,
reconstruct) can now bubble up a typed error instead of aborting
the process.

Also add defensive length and bounds checks in the weighted
Reconstructable impls so that a malformed share vector is rejected
before indexing the virtual-player space.

All internal DKG call sites that iterate over trusted player ids
derived from sc.get_player(i) retain the invariant via .expect,
keeping the change footprint small for the existing trait surface.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>

* [consensus] Validate SecretShare structure before crypto verification

A malicious validator could send a SecretShare with a share vector
shorter than its author's expected weight, or with a player id that
does not match the author's validator index. Prior to this change
the optimistic-verification fast path accepted such shares and
relied on a later panicking index into the virtual-player space,
which crashed the node from inside spawn_blocking.

verify_structural now checks:
- share.share.0.id matches the author's validator index
- share.share.1.len() equals the author's expected weight

before deferring to the (expensive) cryptographic verification.
Tests cover shorter-than-expected and longer-than-expected vectors,
player-id mismatch, and author-mismatch. A regression test in the
share store bypasses verify_structural to exercise the downstream
defense-in-depth path in reconstruct.

_Trimmed to 38 lines — full report: https://github.com/aptos-labs/aptos-core/commit/b4ca925a9e657868dc6a1cceaeef3c70c036e6b1_
