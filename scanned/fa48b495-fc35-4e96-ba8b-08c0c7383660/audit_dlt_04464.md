# [M] depositAuction can revert in underflow in step 4

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/165
Type: sherlock-finding

## Details
ctf_sec

medium

# depositAuction can revert in underflow in step 4

## Summary

depositAuction can revert in underflow in step 4

## Vulnerability Detail

the function depositAuction is used  totaking in orders from mm's to buy sqth and depositing the usd amount from the depositQueue into crab along with the eth from selling sqth

this the 6 steps:

```solidity
/**
 * step 1: get eth from mm
 *     step 2: get eth from deposit usdc
 *     step 3: crab deposit
 *     step 4: flash deposit
 *     step 5: send sqth to mms
 *     step 6: send crab to depositors
 */
```

If we look into step 2, step 3, and step 4

```solidity
 // step 2
  ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
      tokenIn: usdc,
      tokenOut: weth,
      fee: _p.ethUSDFee,
      recipient: address(this),
      deadline: block.timestamp,
      amountIn: _p.depositsQueued,
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/165_
