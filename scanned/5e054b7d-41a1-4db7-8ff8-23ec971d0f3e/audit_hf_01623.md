# [C] An attacker can steal any user's cvETH

## Summary
Severity: Critical
Contest weight: 0.5372
Dataset id: 8729
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The cvToken::repay() function allows a user to specify the payer while repaying the minted cvETH. However, there is no authorization check to ensure that msg.sender is authorized to spend the payer's cvETH. As a result, an attacker can use any user's cvETH to repay their own minted cvETH, effectively stealing the user's funds.

## Recommendation
Add allowance check to repay function.
```solidity
function repay(address payer, address target, uint256 amount) public
    nonReentrant whenNotPaused returns (uint256) {
    if (amount <= 0) {
        revert Errors.InvalidAmount();
    }
    if (payer != msg.sender)
        _spendAllowance(payer, msg.sender, amount);
    return _repay(payer, target, amount, true);
}
```
