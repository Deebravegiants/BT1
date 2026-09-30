# [M] A malicious attacker can create

## Summary
Severity: Medium
Contest weight: 0.4115
Dataset id: 1893
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user creates an order in the OracleLess contract, he can add a malicious token contract that reverts when tokens are transferred from the OracleLess contract. This order can't be canceled by admin. A malicious attacker can create this kind of order as many as he can to grieve the protocol.  
At OracleLess.sol#L38, there is no restrictions for tokenIn. Any contract that implements IERC20 can be tokenIn.

Internal pre-conditions  
N/A

External pre-conditions  
N/A

Attack Path  
• Alice creates a malicious token contract that reverts if token is transferred from the OracleLess contract.  
• Alice creates orders by using fake token contract.  
• This order can't be cancelable as it reverts at L160.
```solidity
function _cancelOrder(Order memory order) internal returns (bool) {
    //refund tokenIn amountIn to recipient
    order.tokenIn.safeTransfer(order.recipient, order.amountIn);
```

• A malicious attacker can grieve the protocol by making a lot of uncancelable orders.  
• All users of the protocol waste significant gas whenever they fill or cancel orders.

## Recommendation
It is recommended to add mechanism to whitelist tokens.
