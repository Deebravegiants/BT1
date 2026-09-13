# [?] ConnectBlock: fix CVE-2024-52911 use-after-free in script-verify path

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2026-05-07
Source: https://github.com/zcash/zcash/commit/65494c01603957592f28e570a88956bbba525640
Type: security-commit

## Details
ConnectBlock: fix CVE-2024-52911 use-after-free in script-verify path

Move `txdata` declaration above `control` so that LIFO destruction
of automatic objects at function exit guarantees ~CCheckQueueControl
runs first (and Wait()s on script-verify worker threads) while
`txdata` is still alive. Workers hold non-owning
`PrecomputedTransactionData *` pointers into this vector via
`CScriptCheck::txdata`; with the prior declaration order, any
early return between `control.Add(vChecks)` and `control.Wait()` --
for example the `ContextualCheckShieldedInputs` failure path --
would destroy `txdata` first, after which ~CCheckQueueControl
would block on in-flight workers that are still dereferencing
freed memory.

Equivalent in shape to the upstream Bitcoin Core cleanup in
bitcoin/bitcoin#35209 (which fixed the root cause of CVE-2024-52911,
covertly mitigated earlier in bitcoin/bitcoin#31112). zcashd
forked from BC circa 2018 and never received either fix.

Reachable from any inbound P2P peer via a crafted invalid block.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
