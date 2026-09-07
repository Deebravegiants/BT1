# [H] Need alternative methods to hedge and reduce risk

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/214
Type: sherlock-finding

## Details
__141345__

high

# Need alternative methods to hedge and reduce risk

## Summary

Currently the CrabNetting.sol relies on `depositAuction()` and `withdrawAuction()` to hedge the position. However, in severe market conditions against the strategy, the hedge might not work as expected, because the auction relies on enough market counter parties. If case of not enough market liquidity, users have to suffer loss. 


## Vulnerability Detail

The crab strategy rebalance require enough counter parties in the market. Currently the auction use discounted price than uniswap to create incentives for counter parities. But it is possible that the market is extreme so that traders are completely not likely to open new positions. Or the slippage might deviate too much exceeding the max allowable tolerance (common in extreme markets).


#### scenario 1: up market

Imagine ETH price to the moon, but the volatility is low (low funding rate).
In this case, crab strategy needs to long ETH, (buy Squeeth, burn crab token), call `withdrawAuction()`.

- For traders who long Squeeth 
They are making big profit from the up market, likely to have more incentive to hold rather than sell. Or the slippage could be big.

- For traders who short Squeeth 
In up market, short ETH^2 with low funding rate is losing money, so low incentives for them to mint new  Squeeth.

- Uniswap LP
In single side market, impermanent loss is big, especially for concentrated LP in V3. As a result, liquidity providers are prone to withdraw the LP.

In summary, when ETH price skyrockets, those who short Squeeth face the risk of liquidation. But the auction takes time, and in extreme markets, each kind of traders lack the incentive to be the counter party to sell Squeeth to the crab contract. 

And the users already send the crab tokens into the contract in `queueCrabForWithdrawal()`, when `isAuctionLive` is true, they can not withdraw. If the auction does not succeed, the loss will be bigger.

Some mitigation might be, the admin takes immediate action to directly add collateral to avoid liquidation. 


#### scenario 2: crash market

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/214_
