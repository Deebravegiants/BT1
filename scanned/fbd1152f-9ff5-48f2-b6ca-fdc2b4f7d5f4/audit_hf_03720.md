# [M] Insufficient oracle validation

## Summary
Severity: Medium
Contest weight: 0.4031
Dataset id: 19839
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Most prices are provided by an off-chain oracle archive via signed prices, but a
Chainlink oracle is still used for index prices. These prices are insufficiently
validated.
There is no freshness check on the timestamp of the prices, so old prices may be
used if OCR was unable to push an update in time
Old prices mean traders will get wrong PnL values for their positions, leading to
liquidations or getting more/less than they should, at the expense of other traders
and the liquidity pools.
The timestamp field is ignored, which means there's no way to check whether the
price is recent enough:
```solidity
// File: gmx-synthetics/contracts/oracle/Oracle.sol :
Oracle._setPricesFromPriceFeeds()
    (
        /* uint80 roundID */,
        int256 _price,
        /* uint256 startedAt */,
        /* uint256 timestamp */,
        /* uint80 answeredInRound */
    ) = priceFeed.latestRoundData();
```

## Recommendation
Add a staleness threshold number of seconds configuration parameter, and ensure
that the price fetched is within that time range
