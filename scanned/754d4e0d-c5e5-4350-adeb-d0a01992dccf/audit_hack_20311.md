# [M] 5.2.19 Add extra 0 checks inverifyAggregateRoot()andproveMessageRoot().

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** SpokeConnector.sol#L403-L422, SpokeConnector.sol#L456-L481
**Description:** The functionsverifyAggregateRoot()andproveMessageRoot()verify and confirm roots. A root
value of 0 is a special case. If this value would be allowed, then the functions could allow invalid roots to be passed.
Currently the functionsverifyAggregateRoot()andproveMessageRoot()don't explicitly verify the roots are not
0.


```
function verifyAggregateRoot(bytes32 _aggregateRoot) internal {
if (provenAggregateRoots[_aggregateRoot]) {
return;
}
...// do several verifications
provenAggregateRoots[_aggregateRoot] = true;
}
function proveMessageRoot(...) ... {
if (provenMessageRoots[_messageRoot]) {
return;
}
...// do several verifications
provenMessageRoots[_messageRoot] = true;
}
```
**Recommendation:** As an extra safety precaution do the following:

- In functionverifyAggregateRoot()check_aggregateRoot != 0.
- InproveMessageRoot()check_messageRoot != 0.
**Connext:** Solved in PR 2442.
No check added inproveMessageRoot()becausecalculateMessageRoot()never results in 0.
**Spearbit:** Verified.
