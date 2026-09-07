# [?] Fix postgres DoS advisories (RUSTSEC-2026-0178/0179/0180) (#26968)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-06-15
Source: https://github.com/MystenLabs/sui/commit/14c59d81505b738529ab7013b21cc2341adce79d
Type: security-commit

## Details
Fix postgres DoS advisories (RUSTSEC-2026-0178/0179/0180) (#26968)

## Summary

Three `vulnerability`-class advisories (published Jun 12) are currently
failing `cargo-deny advisories` on `main`, so every rust-touching PR
shows red. All are in the transitive postgres stack and have patched
releases:

| Advisory | Crate | Fix |
|---|---|---|
| RUSTSEC-2026-0179 | `postgres-protocol` 0.6.7 → **0.6.12** | SCRAM
CPU-exhaustion DoS |
| RUSTSEC-2026-0180 | `postgres-protocol` 0.6.7 → **0.6.12** | `hstore`
panic DoS |
| RUSTSEC-2026-0178 | `tokio-postgres` 0.7.12 → **0.7.18** | `DataRow`
panic DoS |

These come in via `tokio-postgres → bb8-postgres → sui-rpc-benchmark`
(and `sui-pg-db`) — tooling/benchmark crates, not the node binary; the
DoS vector is a malicious postgres *server* attacking the client. Still
real, and `cargo-deny` hard-fails, so this gets `main` green again.

**Lockfile-only — no workspace manifest changes.** The workspace already
declares `tokio-postgres = "0.7.12"` (caret), which permits 0.7.18.

### Why the delta is more than 3 lines

`tokio-postgres 0.7.18` requires `whoami 2.x`, which needs `libredox
>=0.1.12`; the lock had `libredox 0.1.4` pinned (via `filetime ← notify
← sui-data-ingestion-core`). A single-package `--precise` bump can't
move `libredox`, which is what blocked the naive update. Lifting
`libredox` to 0.1.17 (satisfies both `filetime`'s `^0.1.0` and
`whoami`'s `^0.1.12`) unblocks it, pulling these within-range transitive
bumps:

| Crate | Change | Reason |
|---|---|---|

_Trimmed to 38 lines — full report: https://github.com/MystenLabs/sui/commit/14c59d81505b738529ab7013b21cc2341adce79d_
