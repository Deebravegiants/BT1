### Title
Missing Negative Price Validation in `ChainlinkPriceOracle.getAssetPrice()` Allows Corrupted Chainlink Answer to Freeze Deposits and Withdrawals - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` casts the raw `int256 answer` from `latestRoundData()` directly to `uint256` without ver