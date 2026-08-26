# [?] Avoid panic when reorged claims cannot merge

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2026-07-30
Source: https://github.com/lightningdevkit/rust-lightning/commit/f1dc848727639e34cc98b26db32a6059b4bff3aa
Type: security-commit

## Details
Avoid panic when reorged claims cannot merge

Previously, a deep reorg could resurrect an HTLC package at a height
where it was no longer mergeable with its surviving claim. This caused
`OnchainTxHandler::blocks_disconnected` to panic on an assertion.

When merging fails, we now preserve the resurrected package in
`locktimed_packages` so normal block processing registers and broadcasts
it as an independent claim. Add a regression test covering the reorg and
subsequent broadcast.

Thanks to Kyle W. Santiago for reporting this issue.

Co-authored-by: Elias Rohrer <dev@tnull.de>
