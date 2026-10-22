# [M] MToken's total principal invariant can be broken

## Summary
Severity: Medium
Contest weight: 0.4163
Dataset id: 10698
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because there's an unchecked total earning principal addition in MToken._addEarningAmount, the MToken contract would be subject to a potential silent overflow of principalOfTotalEarningSupply. However, there's a check in the MinterGateway.mintM function that's supposed to prevent this from ever happening. But because minterRate and earnerRate can be different, it is possible that a silent overflow happening in MToken doesn't get caught by the check in MinterGateway. The transaction will not be reverted, and principalOfTotalEarningSupply will silently overflow, reaching a broken state. Because a silent overflow in MToken will lead to an additional mint of MinterGateway.excessOwedM, the function can still revert in a safe uint112 cast within MToken.mint. But there's still possible mint amount values which will lead to a successful transaction. Close to the point of overflow, a malicious minter could mint the appropriate amount to make MToken reach the broken state. The overflowed principalOfTotalEarningSupply might still be used to drive further impact to the protocol.

## Recommendation
Use checked addition in _addEarningAmount.
```solidity
function _addEarningAmount(address account_, uint112 principalAmount_)
internal {
unchecked {
_balances[account_].rawBalance += principalAmount_;
}
principalOfTotalEarningSupply += principalAmount_;
}
```
