# [M] Unsafe downcasts can lead to errors

## Summary
Severity: Medium
Contest weight: 0.5543
Dataset id: 8726
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are instances where a function takes a uint256 as an input parameter and within the function is downcasted to a much smaller uint:
```solidity
function _mintHedron(uint256 index, uint256 stakeId) internal virtual
returns(uint256 amount) {
    return IHedron(HEDRON).mintNative(index, uint40(stakeId));
}
```
This is a problem because if the stakeId is bigger than uint40, then only the least significant 40 bits will be used. This can lead to lost data. The same applies for the _stakeGoodAccounting function:
```solidity
function _stakeGoodAccounting(uint256 stakeIdParam) internal {
    // no data is marked during good accounting, only computed and placed into logs
    // so we cannot return anything useful to the caller of this method
    UnderlyingStakeable(TARGET).stakeGoodAccounting(stakerAddr, stakeIndex, uint40(stakeIdParam)); //@audit typecast error
}
```

## Recommendation
Be consistent with uints. Change the input parameters to the specific uint (uint40 for example) to avoid losing any data and undesirable scenarios.
