# [M] Operator can backrun owner to avoid chang-

## Summary
Severity: Medium
Contest weight: 0.3985
Dataset id: 20220
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Operator can backrun owner to avoid changing operator. It's possible because transferOperator function can be called by both of them. Agent contract extends Operatable. This is because owner of agent can delegate maintenance of agent to operator. Because of that owner should be able to change operator when he wants. It's 2 step process: set pending operator and then this operator should approve it. For this purpose owner has transferOperator function. ble.sol#L56-L58
```solidity
function transferOperator(address newOperator) public virtual onlyOwnerOperator {
    pendingOperator = newOperator;
}
```
The problem is that operator also can call this function. As result operator can call it right after owner proposed new operator in order to set it to 0. In such way operator can not allow owner to change it. Changing of operator can be blocked by current operator.

## Recommendation
Make transferOperator be callable by owner only.
