# [M] PriceOracle will use the wrong price if the Chain-

## Summary
Severity: Medium
Contest weight: 0.5645
Dataset id: 20048
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Chainlink aggregators have a built in circuit breaker if the price of an asset goes outside of a predetermined price band. The result is that if an asset experiences a huge drop in value (i.e. LUNA crash) the price of the oracle will continue to return the minPrice instead of the actual price of the asset. This would allow user to continue borrowing with the asset but at the wrong price. This is exactly what happened to Venus on BSC when LUNA imploded. acceptable range.

```solidity
function getPriceFromChainlink(address base, address quote) internal view returns (uint256) {
    (int256 price,) = registry.latestRoundData(base, quote);
    require(price > 0, "invalid price");
    // Extend the decimals to 1e18.
    return uint256(price) * 10 ** (18 - uint256(registry.decimals(base, quote)));
}
```

/oracle/PriceOracle.sol#L66-L72 A similar issue is seen here. The wrong price may be returned in the event of a market crash. An adversary will then be able to borrow against the wrong price and incur bad debt to the protocol.

## Recommendation
Implement the proper check for each asset. It must revert in the case of bad price.

```solidity
function getPriceFromChainlink(address base, address quote) internal view returns (uint256) {
    (int256 price,) = registry.latestRoundData(base, quote);
    // use the proper minPrice and maxPrice for each asset
    // Extend the decimals to 1e18.
    return uint256(price) * 10 ** (18 - uint256(registry.decimals(base, quote)));
}
```
