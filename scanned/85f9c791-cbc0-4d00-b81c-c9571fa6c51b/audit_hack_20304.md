# [M] 5.2.9 Relayer could lose funds

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** BridgeFacet.sol#L828-L835
**Description:** ThexReceivefunction on the receiver side can contain unreliable code which Relayer is unaware
of. In the future, more relayers will participate in completing the transaction.
Consider the following scenario:

1. Say thatRelayer Aexecutes thexReceivefunction on receiver side.
2. In thexReceivefunction, a call to withdraw function in a foreign contract is made whereRelayer Ais holding
    some balance.
3. If this foreign contract is checkingtx.origin(say deposit/withdrawal were done via third party), thenRelayer
    A's funds will be withdrawn without his permission (since tx.origin will be the Relayer).
**Recommendation:** Relayers should be advised to use an untouched wallet address so that foreign code interac-
tion cannot harm them.
**Connext:** To be documented, relayers EOA should be single-purpose.
**Spearbit:** Acknowledged.
