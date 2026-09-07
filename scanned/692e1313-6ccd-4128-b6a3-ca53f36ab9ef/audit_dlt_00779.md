# [?] Fix rpc hash race condition (#3693)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2026-07-02
Source: https://github.com/sei-protocol/sei-chain/commit/ae66b4fe0b5812c1287cb67e79786533abca5b56
Type: security-commit

## Details
Fix rpc hash race condition (#3693)

## Fix
Serialize the hash-mutating operations on each memIAVL tree with the
tree's
**write** lock, and add no-lock internal helpers so the public entry
points
don't re-acquire the lock recursively.
`sei-db/state_db/sc/memiavl/tree.go`
- `RootHash()` now takes `t.mtx.Lock()` (it mutates `MemNode.hash`),
delegating to a new `rootHashNoLock()`.
- `GetProof()` now takes `t.mtx.Lock()` for the whole proof build,
delegating to `getProofNoLock()`.
- Added no-lock read helpers used by the proof builders:
`getWithIndexNoLock()`, `getByIndexNoLock()`, `hasNoLock()`.
`sei-db/state_db/sc/memiavl/proof.go`
- `GetMembershipProof()` / `GetNonMembershipProof()` now take the write
lock and delegate to `getMembershipProofNoLock()` /
`getNonMembershipProofNoLock()`.
- `createExistenceProof()` documented as "caller must hold the write
lock".
The read-only fast paths (`Get`, `GetWithIndex`, `GetByIndex`, `Has`,
`Iterator`)
are unchanged and still use `RLock`. Locking is **per-tree
(per-store)**.
### Lock-ordering safety
- Commit path acquires `db.mtx` then per-tree `t.mtx`; the query path
acquires
  only `t.mtx`. No inversion, no new deadlock.
- No in-package caller invokes the now-locking methods while already
holding
  `t.mtx` (verified); internal callers use the `*NoLock` helpers.
## Performance impact
- **Validators (no queries):** the write lock is uncontended, so
`Lock()` costs
the same as the previous `RLock()` (a single atomic op). `RootHash` runs
~once/twice per store per block → single-digit microseconds per block.
No

_Trimmed to 38 lines — full report: https://github.com/sei-protocol/sei-chain/commit/ae66b4fe0b5812c1287cb67e79786533abca5b56_
