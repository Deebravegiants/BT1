# [?] node/cn: fix nil deref race in sidecarReqManager.update

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2026-04-13
Source: https://github.com/kaiachain/kaia/commit/534db158852c93e0482350a91bb06d41171ae097
Type: security-commit

## Details
node/cn: fix nil deref race in sidecarReqManager.update

Add a nil guard at the top of update() so that a concurrent delete()
(e.g. handleBlobSidecarsMsg removing the entry just before the sync
loop calls update()) results in a safe no-op instead of a panic.

Also add TestSidecarReqManager_UpdateNilEntry to cover the race path.
