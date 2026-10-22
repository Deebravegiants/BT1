# [M] 5.1.3 FunctionconsolidatePendingState()can be executed during emergency state

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** PolygonZkEVM.sol#L783-L
**Description:** The functionconsolidatePendingState()can be executed by everyone even when the contract is
in an emergency state. This might interfere with cleaning up the emergency.
Most other functions are disallowed during an emergency state.
function consolidatePendingState(uint64 pendingStateNum) public {
if (msg.sender != trustedAggregator) {
require(isPendingStateConsolidable(pendingStateNum),...);
}
_consolidatePendingState(pendingStateNum);
}

**Recommendation:** Consider adding the following, which also improves consistency

```
function consolidatePendingState(uint64 pendingStateNum) public {
if (msg.sender != trustedAggregator) {
+ require(!isEmergencyState,...);
require(isPendingStateConsolidable(pendingStateNum),...);
}
_consolidatePendingState(pendingStateNum);
}
```
**Polygon-Hermez:** Solved in PR 87.
**Spearbit:** Verified.
