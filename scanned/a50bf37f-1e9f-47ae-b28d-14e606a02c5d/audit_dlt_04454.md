# [M] Funds are locked permanently in the CrabNetting contract

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/193
Type: sherlock-finding

## Details
hansfriese

medium

# Funds are locked permanently in the CrabNetting contract

## Summary

In the function `depositAuction` and `withdrawAuction`, the funds are calculated by rounding down and this leaves minor amount of funds (ETH/CRAB/USDC). These are locked in the contract permanently.

## Vulnerability Detail

If we look at the function `depositAuction` of CrabNetting.sol#L584-#L618, CRAB and ETH are sent proportionally to the user's deposit amount.
Because every actual amount is calculated by rounding down, it is possible that not all funds are sent. (Even the ETH amount less than 1e12 are not handled.)
I note that these are permanently locked in the contract because the protocol always operates based on before/after balance difference.

```solidity
// CrabNetting.sol #572
to_send.crab = IERC20(crab).balanceOf(address(this)) - initCrabBalance;//@audit-info crab got from two deposits: normal + flash deposit
// get the balance between start and now
to_send.eth = address(this).balance - initEthBalance;
IWETH(weth).deposit{value: to_send.eth}();

while (remainingDeposits > 0) {
    uint256 queuedAmount = deposits[k].amount;
    Portion memory portion;
    if (queuedAmount == 0) {
        k++;
        continue;
    }
    if (queuedAmount <= remainingDeposits) {
        remainingDeposits = remainingDeposits - queuedAmount;
        usdBalance[deposits[k].sender] -= queuedAmount;

        portion.crab = (((queuedAmount * 1e18) / _p.depositsQueued) * to_send.crab) / 1e18;

        IERC20(crab).transfer(deposits[k].sender, portion.crab);

```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/193_
