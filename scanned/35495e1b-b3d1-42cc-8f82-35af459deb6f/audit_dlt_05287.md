# [?] fix(wallet): do not panic on an unknown consensus item variant

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-06
Source: https://github.com/fedimint/fedimint/commit/6dd783df3ead00a5438c3d33140348fe390f7726
Type: security-commit

## Details
fix(wallet): do not panic on an unknown consensus item variant

`WalletConsensusItem` carries an `#[encodable_default]` variant so that a
peer which predates a new item type can still decode a session log. That
makes decoding deliberately lenient: an unknown discriminant decodes into
`Default { variant, bytes }` rather than failing.

The classic wallet module then treated that variant as unreachable and
panicked on it. A consensus item's discriminant is chosen by whichever
peer proposes it, so a single malicious guardian -- well inside the `f`
of `n = 3f + 1` fault bound -- can put `Default { variant: 99 }` in its
AlephBFT unit batch and panic every honest guardian at once. The panic
unwinds a root task-group task, which trips `TaskPanicGuard::drop` and
exits the process, and because the item never reaches `AcceptedItemKey`
the persisted unit is replayed on restart, so the federation crash-loops
rather than recovering.

`f9034270d` fixed exactly this class one layer up, in the consensus
engine's own `ConsensusItem` dispatch, but the sweep never reached the
per-module handlers. Classic wallet was the last one left: ln, lnv2 and
walletv2 all already return an error here.

Rejecting the item instead of panicking is consensus-safe by the same
argument that fix used. Processing runs identically on every guardian,
so an unknown variant that reached consensus would have panicked all of
them at that ordered item and kept doing so on every restart. A
federation that is still running therefore has no such item in its
history, and the new rejection can only ever fire where the old
behaviour halted the federation instead.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011hiuVTowKNSSYVtxwQTdP9
