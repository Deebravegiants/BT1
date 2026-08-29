# [M] Griefing is possible for depositAuction and netAtPrice

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/153
Type: sherlock-finding

## Details
hyh

medium

# Griefing is possible for depositAuction and netAtPrice

## Summary

As active auction isn't a prerequisite for depositAuction() and netAtPrice(), both functions can be front-run with USDC withdrawal, making them fail asset amount check and revert.

## Vulnerability Detail

If netAtPrice() and depositAuction() be called when an auction is not live, a griefing attack is possible: Bob the depositor can front-run the functions, withdrawing the amount previously deposited, so there will be a deficit and the functions will be failing.

I.e. if an auction isn't started any depositor can manipulate these functions into unavailability. As the amounts need to be recalculated after Bob withdrew his funds this means proceeding with the action somewhat later, potentially in a different market conditions, which can be beneficial to Bob and serves as a reason for the attack. Say Bob can join, monitor and block the auctions with withdrawal based on some condition, having some kind of free option at the expense of other participants as a result.

## Impact

Manipulating netting and auction functions can be used for market timing and, when executed, generate profit for the attacker at the expense of other participants, who meet attackers' orders when it is suitable to him. Due to prerequisite of having `isAuctionLive == false` (say via auction script malfunction or an operational mistake) setting the severity to medium.

## Code Snippet

depositAuction() will fail on the router call if `_p.depositsQueued > IERC20(usdc).balanceOf(address(this))`:

https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L487-L536

```solidity
    /**
     * @dev takes in orders from mm's to buy sqth and deposits the usd amount from the depositQueue into crab along with the eth from selling sqth
     * @param _p DepositAuction Params that contain orders, usdToDeposit, uniswap min amount and fee
     */
    function depositAuction(DepositAuctionParams calldata _p) external onlyOwner {
        _checkOTCPrice(_p.clearingPrice, false);
        /**
         *     step 1: get eth from mm
         *     step 2: get eth from deposit usdc
         *     step 3: crab deposit
         *     step 4: flash deposit
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/153_
