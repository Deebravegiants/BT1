# [?] fix: prevent PoA leader deadlock after reconciliation import (#3261)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2026-04-16
Source: https://github.com/FuelLabs/fuel-core/commit/0faeb99ce1d01743838394acaacf64907aba5a24
Type: security-commit

## Details
fix: prevent PoA leader deadlock after reconciliation import (#3261)

## Summary

- Fixes a deadlock in the PoA service that caused a 30-minute block
production outage on testnet (April 9, 2026)
- After a FENCING_ERROR, reconciliation imports a block via
`execute_and_commit` which marks it as `Source::Network`. The SyncTask
sees this and transitions from `Synced` → `NotSynced`. On the next
iteration, `ensure_synced()` blocks forever — the leader can't produce
while blocked, and the SyncTask needs a locally-produced block to
recover. Classic deadlock.
- Fix: add a reconciliation watermark (`Arc<AtomicU32>`) shared between
`MainTask` and `SyncTask`. Before importing reconciliation blocks,
`MainTask` sets the watermark to the max height. `SyncTask` treats
blocks at heights ≤ the watermark as locally produced, staying `Synced`.

## Details

**Root cause chain:**
1. `importer.rs:584-585` — `execute_and_commit` always uses
`ImportResult::new_from_network()`
2. `sync.rs:186-203` — SyncTask transitions `Synced → NotSynced` on
non-local block with height > current
3. `service.rs:501-521` — `ensure_synced()` blocks on
`sync_state.changed()` when `NotSynced`
4. Deadlock: leader blocked in `ensure_synced()`, SyncTask waiting for
locally-produced block that can never arrive

**Why a watermark:** A bool flag has a race condition — the SyncTask may
not poll the broadcast channel until after the flag is cleared. The
watermark encodes a permanent fact ("all blocks up to height N were
reconciled") that never needs clearing.

**Files changed (all within `fuel-core-poa`):**
- `sync.rs` — Add `reconciliation_watermark` field, check it in block
handler
- `service.rs` — Create shared watermark, set via `fetch_max` during

_Trimmed to 38 lines — full report: https://github.com/FuelLabs/fuel-core/commit/0faeb99ce1d01743838394acaacf64907aba5a24_
