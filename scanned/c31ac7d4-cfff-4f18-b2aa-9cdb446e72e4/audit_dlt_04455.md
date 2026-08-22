# [M] withdrawAuction can distribute extra USDC to withdrawer queue

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/192
Type: sherlock-finding

## Details
hyh

medium

# withdrawAuction can distribute extra USDC to withdrawer queue

## Summary

withdrawAuction() doesn't check that the needed amount of squeeth is obtained from the orders supplied. If the amount isn't reached, the squeeth from the balance will be used instead.

## Vulnerability Detail

There is no check in withdrawAuction() that `toPull` is zero, which allow for the situation when `ICrabStrategyV2(crab).getWsqueethFromCrabAmount(_p.crabToWithdraw)` requested will not be gathered from the orders supplied to the call.

If there are no squeeth on the balance the function will revert on `ICrabStrategyV2(crab).withdraw(_p.crabToWithdraw)` call.

If there were leftover squeeth funds on the CrabNetting's balance those funds will be send over to the withdrawers queued.

## Impact

Squeeth funds from CrabNetting's balance will be distributed to the current withdrawers queue in USDC form. That's a violation of protocol logic (USDC distributed should be determined by the price and stake), and is a loss of funds for the protocol.

Setting the severity to medium due to prerequisite of squeeth shortage in the provided orders.

## Code Snippet

withdrawAuction() will proceed with `ICrabStrategyV2(crab).withdraw(_p.crabToWithdraw)` even when `toPull > 0`:

https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L624-L657

```solidity
    /**
     * @dev takes in orders from mm's to sell sqth and withdraws the crab amount in q
     * @param _p Withdraw Params that contain orders, crabToWithdraw, uniswap min amount and fee
     */
    function withdrawAuction(WithdrawAuctionParams calldata _p) public onlyOwner {
        _checkOTCPrice(_p.clearingPrice, true);
        uint256 initWethBalance = IERC20(weth).balanceOf(address(this));
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/192_
