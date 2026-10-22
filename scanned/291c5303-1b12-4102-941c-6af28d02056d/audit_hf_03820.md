# [M] Wrong Price will be Returned When Asset is

## Summary
Severity: Medium
Contest weight: 0.4610
Dataset id: 20050
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Iron Bank allows a PToken market to be created for an underlying asset in addition to a lending market. PTokens can be counted as user collaterals and their price is fetched based on their underlying tokens. However, wrong price will return when PToken's underlying asset is WstETH. Retrieving price for WstETH is a 2 step process. WstETH needs to be converted to market is WstETH through checking if (asset == wsteth). But when PToken market is created for WstETH, this check will be bypassed because PToken contract address will be different from wsteth address. PToken market price is set through _setAggregators() in PriceOracle.sol where base and quote token address are set and tested before writing into aggregators. Price is accessed through getPrice(), if the input asset is not wsteth address, aggregators is directly pulled to get chainlink price denominated in ETH or USD.

```solidity
// PriceOracle.sol
// _setAggregators()
require(
    aggrs[i].quote == Denominations.ETH ||
    aggrs[i].quote == Denominations.USD,
    "unsupported quote"
);

// PriceOracle.sol
function getPrice(address asset) external view returns (uint256) {
    if (asset == wsteth) {
        uint256 stEthPrice = getPriceFromChainlink(
            steth,
            Denominations.USD
        );
        uint256 stEthPerToken = WstEthInterface(wsteth).stEthPerToken();
        uint256 wstEthPrice = (stEthPrice * stEthPerToken) / 1e18;
        return getNormalizedPrice(wstEthPrice, asset);
    }
    AggregatorInfo memory aggregatorInfo = aggregators[asset];
    uint256 price = getPriceFromChainlink(
        aggregatorInfo.base,
        aggregatorInfo.quote
    );
    ...
}
```

This creates a problem for PToken for WstETH, because if (asset == wsteth) will be bypassed and chainlink aggregator price will be returned. And chainlink doesn't have a direct price quote of WstETH/ETH or WstETH/USD, only WstETH/stETH or stETH/USD. This means most likely aggregator price for stETH/USD will be returned as price for WstETH. Since stETH is a rebasing token, and WstETH:stETH is not 1 to 1, this will create a wrong valuation for users holding PToken for WstETH as collaterals. Since users holding PToken for WstETH will have wrong valuation, this potentially creates opportunities for malicious over-borrowing or unfair liquidations, putting the protocol at risk.

## Recommendation
In getPrice(), consider adding another check whether the asset is PToken and its underlying asset is WstETH. If true, use the same bypass for pricing.
