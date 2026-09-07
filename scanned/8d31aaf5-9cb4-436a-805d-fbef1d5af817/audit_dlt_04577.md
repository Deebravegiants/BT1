# [M] Bypassing the `minFee` on `initiateTrade()`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-buffer
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/99
Type: sherlock-finding

## Details
Ch_301

medium

# Bypassing the `minFee` on `initiateTrade()`

## Summary
The ERC20 tokens don't have the same **decimals** so you need to get it before doing any checks 
## Vulnerability Detail
In case of trad with BFR pool the user will be paying and winning in BFR.
So the `BufferRouter.initiateTrade()` will transfer **BFR** 
```solidity
        IERC20(optionsContract.tokenX()).transferFrom(
            msg.sender,
            address(this),
            totalFee
        );
```
Before this `transferFrom()` 
We have this check 

```solidity
optionsContract.runInitialChecks(slippage, period, totalFee);`
```
On `BufferBinaryPool.runInitialChecks()` it’s check the `totalFee >= config.minFee()`
```solidity
    function runInitialChecks(
        uint256 slippage,
        uint256 period,
        uint256 totalFee
    ) external view override {
        require(!isPaused, "O33");
        require(slippage <= 5e2, "O34");
        require(period >= config.minPeriod(), "O21");
        require(period <= config.maxPeriod(), "O25");
        require(totalFee >= config.minFee(), "O35");
    }

```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/99_
