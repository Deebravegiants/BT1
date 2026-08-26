# [?] p2p/discover: p2p/discover: fix crash when revalidated node is removed (#29864)

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2024-05-28
Source: https://github.com/etclabscore/core-geth/commit/e2585cab66d298df1d311e39abf5ab8bcafba15e
Type: security-commit

## Details
p2p/discover: p2p/discover: fix crash when revalidated node is removed (#29864)

In #29572, I assumed the revalidation list that the node is contained in could only ever
be changed by the outcome of a revalidation request. But turns out that's not true: if the
node gets removed due to FINDNODE failure, it will also be removed from the list it is in.
This causes a crash.

The invariant is: while node is in table, it is always in exactly one of the two lists. So
it seems best to store a pointer to the current list within the node itself.
