# [M] Flash deposit part of depositAuction can be prevented

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/238
Type: sherlock-finding

## Details
hyh

medium

# Flash deposit part of depositAuction can be prevented

## Summary

Bob the attacker can send excess WETH to the contract, preventing flash deposit of depositAuction().

## Vulnerability Detail

This is griefing attack that prevents depositors from receiving more crab, providing them with eth instead.

## Impact

Attacker can disturb the auction at will.

As flash deposit sells some sqeeth to obtain more crab the impact is less crab created, depositors are receiving less crab than planned and more eth as initial eth balance didn't included weth.

Partial loss of funds as those users will have to buy crab manually with bigger slippage. An attacker can benefit here by manipulating crab-eth pool.

## Code Snippet

depositAuction() do nothing if `to_send.eth > _p.ethToFlashDeposit > 0`:

https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L539-L551

```solidity
        // step 3
        IWETH(weth).withdraw(IWETH(weth).balanceOf(address(this)));
        ICrabStrategyV2(crab).deposit{value: _p.totalDeposit}();

        // step 4
        Portion memory to_send;
        to_send.eth = address(this).balance - initEthBalance;
        if (to_send.eth > 0 && _p.ethToFlashDeposit > 0) {
            if (to_send.eth <= _p.ethToFlashDeposit) {
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/238_
