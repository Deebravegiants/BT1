# [M] Strategist can transfer user funds to themselves

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-05-rubicon
Published: 2022-05-25
Source: https://github.com/code-423n4/2022-05-rubicon-findings/issues/51
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-rubicon/blob/main/contracts/rubiconPools/BathPair.sol#L324


# Vulnerability details

## Impact
The strategist is able to use user funds to trade on the RubiconMarket. They can abuse this to transfer user funds to themselves.

A strategist having access to user funds seems to be a deliberate design choice. But, I believe it's important to note how dangerous that is.

## Proof of Concept
1. Strategist opens up an offer through [placeMarketMakingTrades()](https://github.com/code-423n4/2022-05-rubicon/blob/main/contracts/rubiconPools/BathPair.sol#L324) where a token is sold for very cheap
2. Strategist accepts the offer within the same transaction using their private wallet

## Tools Used
none

## Recommended Mitigation Steps
There's no easy way to fix this since it's a big part of the protocol. You'd have to overhaul the whole thing.

You could minimize the dmg by limiting the amount of funds a strategist has access to
