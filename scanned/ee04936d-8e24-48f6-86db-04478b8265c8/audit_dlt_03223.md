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

        emit TreasuryApproval(token, spender, amount);
    }    
```

From the above code we can see that when executed `gscApprove` consumes `gscAllowance[]`
and ultimately uses `IERC20(token).approve();` to give the `spender` allowance

Since the direct use is `IERC20.approve(spender, amount)`, the amount of the allowance is overwritten, whichever comes last

In the other methods `approveSmallSpend`,`approveMediumSpend`,`approveLargeSpend`
also use `IERC20(token).approve();`, which causes them to override each other if targeting the same `spender`.

Even if there is a malicious `GSC_CORE_VOTING_ROLE`, it is possible to execute `gscApprove(amount=1 wei)` after `approveLargeSpend()` to reset to an allowance of only `1 wei`.


The recommendation is to use accumulation to avoid, intentionally or unintentionally, overwriting each other

## Tools Used

## Recommended Mitigation Steps

```solidity
    function _approve(address token, address spender, uint256 amount, uint256 limit) internal {
        // check that after processing this we will not have spent more than the block limit
        uint256 spentThisBlock = blockExpenditure[block.number];
        if (amount + spentThisBlock > limit) revert T_BlockSpendLimit();
        blockExpenditure[block.number] = amount + spentThisBlock;

        // approve tokens
-      IERC20(token).approve(spender, amount);
+      uint256 old = IERC20(token).allowance(address(this),spender);
+      IERC20(token).approve(spender,  old + amount);

        emit TreasuryApproval(token, spender, amount);
    } 
```


## Assessed type

Context
