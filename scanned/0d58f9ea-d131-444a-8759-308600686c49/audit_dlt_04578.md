# [M] The `handler` can’t `provideForAccount()`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-buffer
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/98
Type: sherlock-finding

## Details
Ch_301

medium

# The `handler` can’t `provideForAccount()`

## Summary
The **handler** is a  `RewardRouter` Contract (Forked from the GMX Staking contracts) which is not part of the Audit Scope as the team said. Only the `DEFAULT_ADMIN_ROLE` can add or remove **handlers** from `isHandler[ ]`, so you need to trust the Admin but this is not the main case. In case you want to provide liquidity for another account, you can’t transfer the ERC20 tokens from another account without permissions   


## Vulnerability Detail
Only the **handler** can invoke `BufferBinaryPool.provideForAccount()`
On `_provide()` these lines  
```solidity
        bool success = tokenX.transferFrom(
            account,
            address(this),
            tokenXAmount
        );
```
In case `BufferBinaryPool` doesn’t have the `approve()` from the `account` it will revert, this is the case one
But in case the **handler** is supposed to provide liquidity for the `account`
The logic needs to be 
```solidity
        bool success = tokenX.transferFrom(
            msg.sender(),
            address(this),
            tokenXAmount
        );
```

## Impact
`BufferBinaryPool.provideForAccount()` will fail to deliver the flow

## Code Snippet
```solidity
    function provideForAccount(
        uint256 tokenXAmount,
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/98_
