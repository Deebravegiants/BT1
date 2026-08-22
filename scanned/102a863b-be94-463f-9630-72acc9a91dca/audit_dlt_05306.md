# [?] fix(mint): avoid panic on duplicate blind nonce in recovery index (#8533)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-04-21
Source: https://github.com/fedimint/fedimint/commit/a9068911434fa85051306cd5c52ef5a25e64b2ce
Type: security-commit

## Details
fix(mint): avoid panic on duplicate blind nonce in recovery index (#8533)

## Summary

The `RecoveryBlindNonceOutpointKey → OutPoint` index in
`fedimint-mint-server` was being populated with `insert_new_entry` in
two places, both of which panic the guardian on a duplicate blind nonce:

- `migrate_db_v2` backfill
(`modules/fedimint-mint-server/src/lib.rs:494-498`) — walks module
history on first v0.11 start and builds the index from every
`ModuleHistoryItem::Output`.
- Live `process_output` path
(`modules/fedimint-mint-server/src/lib.rs:669-673`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
