# [M] Funds will be lost for Swivel lend() caller if it be run with another Yield Space pool and zero premiumSlippage

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/149
Type: sherlock-finding

## Details
hyh

medium

# Funds will be lost for Swivel lend() caller if it be run with another Yield Space pool and zero premiumSlippage

## Summary

Swivel version of lend() doesn't check the pool provided, `y`, to be the correct pool for the underlying and maturity. if a user mistakingly supplied non-malicious, but incorrect pool for lend() due to operational mistake (say provided otherwise correct pool, but corresponding to some another maturity), and set `premiumSlippage` to be zero, the PT tokens obtained from premium swap will be fully lost for the caller.

## Vulnerability Detail

Swivel lend() will evaluate how much `IMarketPlace(marketPlace).token(u, m, p)` PTs was gained in total from Swivel orders executed and the selling of the premium, minting the same amount of Illuminate PTs to the caller.

If Yield Space pool provided does not correspond to the `(u, m)` combination, being otherwise correct, swivelLendPremium() will mint another type of PT, which will be unaccounted for Illuminate PT quantity calculation and not minted, i.e. it will be lost for the user.

## Impact

If there is the PT in the system that `y` pool produced a redeem for it can be called thereafter and these funds will be socialized among the holders of the corresponding Illuminate PT shares.

If there is no such PT that the `y` pool produced in Illuninate (i.e. no such market was created via `createMarket`), these tokens will be permanently frozen on Lender's balance.

In both cases the funds are lost permanently for the user. However, setting the severity to be medium as the prerequisite is the misconfiguration of the parameters. Notice that its probability isn't low, as it is enough, for example, to use a pool of any wrong maturity, all other things being correct.

## Code Snippet

Swivel lend() calls swivelLendPremium() to sell the underlying left after Swivel orders were filled:

https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/Lender.sol#L349-L449

```solidity
    /// @notice lend method signature for Swivel
    /// @param p principal value according to the MarketPlace's Principals Enum
    /// @param u address of an underlying asset
    /// @param m maturity (timestamp) of the market
    /// @param a array of amounts of underlying tokens lent to each order in the orders array
    /// @param y Yield Space Pool for the Illuminate PT in this market
    /// @param o array of Swivel orders being filled
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/149_
