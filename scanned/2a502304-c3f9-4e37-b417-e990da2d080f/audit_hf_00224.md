# [M] `NestedFactory.sol#_submitInOrders`

## Summary
Severity: Medium
Contest weight: 0.4252
Dataset id: 1149
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When executing orders, the actual `amountSpent + feesAmount` can be lower than `_inputTokenAmount`, the unspent amount should be returned to the user.

However, in the current implementation, the unspent amount will be taken as part of the fee. [`NestedFactory.sol` L285-L309](https://github.com/code-423n4/2021-11-nested/blob/f646002b692ca5fa3631acfff87dda897541cf41/contracts/NestedFactory.sol#L285-L309)

```solidity
function _submitInOrders(
    uint256 _nftId,
    IERC20 _inputToken,
    uint256 _inputTokenAmount,
    Order[] calldata _orders,
    bool _reserved,
    bool _fromReserve
) private returns (uint256 feesAmount, IERC20 tokenSold) {
    _inputToken = _transferInputTokens(_nftId, _inputToken, _inputTokenAmount, _fromReserve);
    uint256 amountSpent;
    for (uint256 i = 0; i < _orders.length; i++) {
        amountSpent += _submitOrder(address(_inputToken), _orders[i].token, _nftId, _orders[i], _reserved);
    }
    feesAmount = _calculateFees(_msgSender(), amountSpent);
    assert(amountSpent <= _inputTokenAmount - feesAmount); // overspent

    // If input is from the reserve, update the records
    if (_fromReserve) {
        _decreaseHoldingAmount(_nftId, address(_inputToken), _inputTokenAmount);
    }

    _handleUnderSpending(_inputTokenAmount - feesAmount, amountSpent, _inputToken);

    tokenSold = _inputToken;
}
```

## Recommendation
No recommendation
