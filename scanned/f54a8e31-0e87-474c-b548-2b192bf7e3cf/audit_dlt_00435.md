# [?] fix(grandpa): GRANDPA panic when a change block is finalized concurrently during justification import (#12506)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2026-08-18
Source: https://github.com/paritytech/polkadot-sdk/commit/34a14dab9628f029a0ef0c457f4fa3a51cd6669a
Type: security-commit

## Details
fix(grandpa): GRANDPA panic when a change block is finalized concurrently during justification import (#12506)

#### Description
A GRANDPA node can panic during block import with:
```
panicked at 'returns Ok when no authority set change should be enacted; qed;', /root/.cargo/git/checkouts/polkadot-sdk-dee0edd6eefa0594/2e4dd0b/substrate/client/consensus/grandpa/src/import.rs:859
```
This is a time-of-check/time-of-use race in
`GrandpaBlockImport::import_justification`. When importing a
justification for a block that enacts a standard authority set change,
the method:

1. reads the current set id and authorities and verifies the
justification against them (acquiring and **releasing** the
authority-set lock), then
2. separately calls `environment::finalize_block`, which re-acquires the
lock to enact the change.

If another finalizer (the voter acting on a gossiped commit, or a
justification imported via sync) finalizes the **same** block in the
window between (1) and (2), then `finalize_block` short-circuits on its
"already finalized in the canonical chain" guard and returns `Ok(())`,
while the caller was told the block enacts a change (`enacts_change ==
true`). The `Ok(_)` arm then trips `assert!(!enacts_change)` and the
node panics.

The window is widened by anything that delays block import relative to
finality — e.g. a `BlockAnnounceValidator` that returns an error/skip
for a while — which lines the two finalizers up on a session-rotation
(change-enacting) block. Observed in logs as the import-path
`finalize_block` hitting the re-finalization guard right after the voter
applied the change:

```
2026-06-29 13:56:48 2026-06-29 11:56:48.072 DEBUG tokio-rt-worker grandpa: Completed round 20, state = State { prevote_ghost: Some((0x8852da3251a16eddb6b583e0e7fdf7c1eeb627b275a12b90c5fefba29d6d95cd, 26)), finalized: Some((0x8852da3251a16eddb6b583e0e7fdf7c1eeb627b275a12b90c5fefba29d6d95cd, 26)), estimate: Some((0x8852da3251a16eddb6b583e0e7fdf7c1eeb627b275a12b90c5fefba29d6d95cd, 26)), completable: true }, step = None    
2026-06-29 13:56:48 2026-06-29 11:56:48.072 DEBUG tokio-rt-worker grandpa: Round 20: prevotes: 3/3/3 weight, 3/3 actual    
2026-06-29 13:56:48 2026-06-29 11:56:48.072 DEBUG tokio-rt-worker grandpa: Round 20: precommits: 3/3/3 weight, 3/3 actual    
2026-06-29 13:56:48 2026-06-29 11:56:48.072 DEBUG tokio-rt-worker grandpa: Voter cool-camp-1893 concluded round 20 in set 5. Estimate = Some(26), Finalized in round = Some(26)    
```

_Trimmed to 38 lines — full report: https://github.com/paritytech/polkadot-sdk/commit/34a14dab9628f029a0ef0c457f4fa3a51cd6669a_
