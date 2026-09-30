# [M] StrategyManager functions are not payable

## Summary
Severity: Medium
Contest weight: 0.3874
Dataset id: 8918
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can use StrategyManager to perform their strategies in one transaction and the code allows sending ETH for the transactions:
```solidity
function executeCall(
    address target,
    uint256 value,
    bytes memory data,
    bool allowRevert
) public onlyOwner
    (bool success, bytes memory returnData) = target.call{value: value}
    (data);
    if (!allowRevert) require(success, 'execution reverted');
    return returnData;
```
The issue is that none of the functions of the StrategyManager are payable and there's no payable fallback() or receive() function so there's no way to transfer ETH to StrategyManager address and perform transactions that require sending ETH.

## Recommendation
Mark StrategyManager functions as payable.
