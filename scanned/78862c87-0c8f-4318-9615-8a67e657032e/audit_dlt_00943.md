# [?] fix: Bound MAP_ENTRY descriptor list to prevent memory pool DoS

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-05-12
Source: https://github.com/LedgerHQ/app-ethereum/commit/ce1915487b6a82f6c1ee6138bd7aa870645ea429
Type: security-commit

## Details
fix: Bound MAP_ENTRY descriptor list to prevent memory pool DoS

verify_map_entry_struct() appended every validly-signed map entry to
g_map_entry_list without bound. The list is cleared on
reset_app_context() between transactions, so the growth isn't
permanent, but a host with N legitimately-signed descriptors can call
INS_PROVIDE_MAP_ENTRY repeatedly during a single signing flow and
exhaust the shared app-memory pool, denying allocation to other
features (trusted_name, enum_value, safe_account, gating, GCS).

Cap the list at MAX_MAP_ENTRIES (32). 32 distinct
(chain, contract, selector, id, key) tuples is well above realistic
per-transaction clear-signing needs while keeping the worst-case
footprint around ~3.5 KB.

This only addresses the DoS component of the finding. Replay
protection (binding the descriptor to a per-session challenge in its
signed TLV) requires a backend payload change and is left out of
scope.
