# [M] The liquidity providers can’t keep their BLP save

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-buffer
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/97
Type: sherlock-finding

## Details
Ch_301

medium

# The liquidity providers can’t keep their BLP save

## Summary
The **handler** is a  `RewardRouter` Contract (Forked from the GMX Staking contracts) which is not part of the Audit Scope as the team said. Only the `DEFAULT_ADMIN_ROLE` can add or remove **handlers** from `isHandler[ ]`, so you need to trust the Admin but this is not the main case 

## Vulnerability Detail
You can't just trust the **handler** to transfer **BLP** from the investors 
On `BufferBinaryPool.transferFrom()`
```solidity
        if (isHandler[msg.sender]) {
            _transfer(_sender, _recipient, _amount);
            return true;
        }
```
As we can see the **handler** can transfer any amount from/to any user

Also (The scenario is not supposed to be, but it is possible)
Lat’s say a **handler** provider supplies tokenX to the pool by invoking `BufferBinaryPool.provide()` ==> `_provide()`, so he will be registered on the `liquidityPerUser` mapping. After `lockupPeriod` he will have some `unlockedAmount`
Now the **handler** could invoke `transferFrom()` or `transfer()` directly
The `_transfer()` has an open hook  `_beforeTokenTransfer()` which is supposed to update the `liquidityPerUser` mapping and invoke `_updateLiquidity()`
```solidity
function _beforeTokenTransfer(
        address from,
        address to,
        uint256 value
    ) internal override {
        if (!isHandler[from] && !isHandler[to] && from != address(0)) {
            _updateLiquidity(from);
            require(
                liquidityPerUser[from].unlockedAmount >= value,
                "Pool: Transfer of funds in lock in period is blocked"
            );
            liquidityPerUser[from].unlockedAmount -= value;
            liquidityPerUser[to].unlockedAmount += value;
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/97_
