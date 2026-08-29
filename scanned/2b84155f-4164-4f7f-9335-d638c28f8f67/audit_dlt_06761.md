# [H] Ineffective ReserveRatio Enforcement

## Summary
Severity: High
Chain: Smart contract
Component: 2022-05-rubicon
Published: 2022-05-27
Source: https://github.com/code-423n4/2022-05-rubicon-findings/issues/106
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathPair.sol#L324
https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathPair.sol#L160


# Vulnerability details

## Background

Per whitepaper, ReserveRatio ensures that some amount of pool liquidity is present in the contract at all times. This protects the pools from overutilization by strategists and ensures that a portion of the underlying pool assets are liquid so LPs can withdraw. If the ReserveRatio is set to 50, meaning 50% of a liquidity pool’s assets must remain in the pool at all times.

However, it was possible for the strategists to bypass the Reserve Ratio restriction and utilize all the funds in the pools, causing the pools to be illiquid.

## Proof-of-Concept

Strategists place their market making trades via the  `BathPair.placeMarketMakingTrades` function. This function would first checks if the pool's reserveRatio is maintained before proceeding. If true, strategists will be allowed to place their market making trades with orders with arbitrary pay amount. Strategists could place ask and bid orders with large pay amount causing large amount of funds will be withdrawen from the pools. The root cause is that at the end of the transaction, there is no additional validation to ensure the pools are not overutilization by strategists and the reserve ratio of the pools is maintained.

[https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathPair.sol#L324](https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathPair.sol#L324)

```solidity
function placeMarketMakingTrades(
    address[2] memory tokenPair, // ASSET, Then Quote
    uint256 askNumerator, // Quote / Asset
    uint256 askDenominator, // Asset / Quote
    uint256 bidNumerator, // size in ASSET
    uint256 bidDenominator // size in QUOTES
) public onlyApprovedStrategist(msg.sender) returns (uint256 id) {
    // Require at least one order is non-zero
    require(
        (askNumerator > 0 && askDenominator > 0) ||
            (bidNumerator > 0 && bidDenominator > 0),
        "one order must be non-zero"
    );

    address _underlyingAsset = tokenPair[0];
    address _underlyingQuote = tokenPair[1];

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-05-rubicon-findings/issues/106_
