# [?] p2p/discover: avoid deadlock between waitForNodes and node additions (#21064)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-05-19
Source: https://github.com/erigontech/erigon/commit/687b534a64ef57d174bc0ed09f4cd1a059e73bc5
Type: security-commit

## Details
p2p/discover: avoid deadlock between waitForNodes and node additions (#21064)

This change fixes a deadlock in peer discovery that can happen after the
routing table runs low on nodes and the iterator falls back to
`waitForNodes`. In that state, a node-add path can end up sending on the
table feed while holding the table mutex, while `waitForNodes` is trying
to wake up and reacquire the same mutex. If the timing lines up, both
sides can block each other and discovery stops making progress.

The fix decouples `waitForNodes` from direct feed consumption on the
mutex-taking goroutine. Instead, it subscribes once and forwards feed
activity through a buffered notification channel, so node-add paths are
no longer blocked by the waiter trying to reenter the table lock. A
regression test is included to cover this locking pattern and make sure
node additions continue to complete while `waitForNodes` is active.

https://github.com/ethereum/go-ethereum/issues/34881

---------

Co-authored-by: Alex Sharov <AskAlexSharov@gmail.com>
