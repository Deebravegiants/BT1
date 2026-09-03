# [M] ArcadeTreasury.sol allowance may be override

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-arcade
Published: 2023-07-25
Source: https://github.com/code-423n4/2023-07-arcade-findings/issues/85
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-arcade/blob/f8ac4e7c4fdea559b73d9dd5606f618d4e6c73cd/contracts/ArcadeTreasury.sol#L391


# Vulnerability details

## Impact
direct use of `IERC20(token).approve(spender, amount);` causes the same `spender` allowances to be overridden by each other

## Proof of Concept
In the `gscApprove()` method it is possible to give `spender` a certain allowance

The code is as follows:

```solidity
    function gscApprove(
        address token,
        address spender,
        uint256 amount
    ) external onlyRole(GSC_CORE_VOTING_ROLE) nonReentrant {
        if (spender == address(0)) revert T_ZeroAddress("spender");
        if (amount == 0) revert T_ZeroAmount();

        // Will underflow if amount is greater than remaining allowance
@>      gscAllowance[token] -= amount;

        _approve(token, spender, amount, spendThresholds[token].small);
    } 

    function _approve(address token, address spender, uint256 amount, uint256 limit) internal {
        // check that after processing this we will not have spent more than the block limit
        uint256 spentThisBlock = blockExpenditure[block.number];
        if (amount + spentThisBlock > limit) revert T_BlockSpendLimit();
        blockExpenditure[block.number] = amount + spentThisBlock;

        // approve tokens
@>      IERC20(token).approve(spender, amount);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-arcade-findings/issues/85_
