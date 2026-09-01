# [?] fix: reject Byzantine PoS proposals instead of panicking

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-05-27
Source: https://github.com/Conflux-Chain/conflux-rust/commit/2da8ea1ba7949712c43e8375161c993b61afc161
Type: security-commit

## Details
fix: reject Byzantine PoS proposals instead of panicking

Two consensus-liveness panic vectors closed:

1. `TransactionAuthenticator` methods `unreachable!("reserved variant")`
   on the `_ReservedEd25519` / `_ReservedMultiEd25519` BCS-compat unit
   variants. A Byzantine proposer can BCS-decode a block payload into a
   reserved variant; `Block::deserialize` is hand-rolled and bypasses
   the `BlockUnchecked` safety layer, so the bad variant reaches
   `PosVM::execute_block` → `check_signature_for_user_tx` → `verify()` →
   panic on every honest peer applying the malicious block. Return Err
   instead. The sibling `scheme()` / `public_key_bytes()` /
   `signature_bytes()` / `Display` paths are also made panic-free for
   defense-in-depth; `Scheme::ReservedEd25519` / `ReservedMultiEd25519`
   preserve the historic BCS-tag-to-scheme-byte injectivity.

2. `ProposalMsg::proposer()` `.expect()` on `Block::author()`, called
   from `proposal.rs` and `consensus_msg.rs` network handlers BEFORE
   any verification, panics on a Byzantine `block_type: NilBlock`
   proposal — the hand-rolled `Block::deserialize` preserves
   `block_type` and `vrf_nonce_and_proof` independently, so a peer can
   hand-craft one. Change `proposer()` to return `Option<Author>`;
   reject in both network handlers; reorder `ProposalMsg::verify` to
   run `verify_well_formed` first (rejects NilBlock-as-proposal at the
   door so the VRF branch's author check stays safe).

Same defect class as PR #3508 (`fix/pos-vrf-proposal-panic`); single
Byzantine validator can crash all honest peers via one message in
either family. No on-chain state changes; both fixes ship as
unconditional hotfixes — patched and unpatched nodes both decline to
vote, differing only in panic vs. clean error.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
