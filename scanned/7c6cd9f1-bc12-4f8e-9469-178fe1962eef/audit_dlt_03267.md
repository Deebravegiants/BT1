# [M] `Asset.lotPrice` only uses `oracleTimeout` to determine if the price is stale.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-03
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/17
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/Asset.sol#L140
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/NonFiatCollateral.sol#L52
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/Asset.sol#L61
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/CurveStableCollateral.sol#L57
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/PoolTokens.sol#L287
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/PoolTokens.sol#L235


# Vulnerability details

## Impact

`OracleTimeout` is the number of seconds until an oracle value becomes invalid. It is set in the constructor of `Asset`. And `Asset.lotPrice` uses `OracleTimeout` to determine if the saved price is stale. However, `OracleTimeout` may not be the correct source to determine if the price is stale. `Asset.lotPrice` may return the incorrect price.

## Proof of Concept

`OracleTimeout` is set in the constructor of `Asset`.
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/Asset.sol#L61
```solidity
    constructor(
        uint48 priceTimeout_,
        AggregatorV3Interface chainlinkFeed_,
        uint192 oracleError_,
        IERC20Metadata erc20_,
        uint192 maxTradeVolume_,
        uint48 oracleTimeout_
    ) {
        …
        oracleTimeout = oracleTimeout_;
    }
```

`Asset.lotPrice` use `oracleTimeout` to determine if the saved price is in good standing.
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/Asset.sol#L140
```solidity
    function lotPrice() external view virtual returns (uint192 lotLow, uint192 lotHigh) {
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-reserve-findings/issues/17_
