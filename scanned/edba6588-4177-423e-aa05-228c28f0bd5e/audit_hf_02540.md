# [M] maxOracleUpdateFrequency must be unique for each chainlink feed

## Summary
Severity: Medium
Contest weight: 0.1099
Dataset id: 13541
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The maxOracleUpdateFrequency is currently an immutable variable for each ChainlinkPriceOracle / RedstoneChainlinkPriceOracle. It is used to determine when a Chainlink feed has timed out. However, different Chainlink feeds have different timeouts and the maxOracleUpdateFrequency must be set to the maximum of all timeouts. An oracle with a lower timeout is not recognized as stale until the full maxOracleUpdateFrequency duration has passed. In such a case, an attacker could make use of the outdated price to mint Index shares at a discount or to receive too many funds from redemption.

## Recommendation
Parameters that are unique to each Chainlink feed are stored in the price source mapper contracts (ChainlinkPriceSourceMapper, RedstoneChainlinkPriceSourceMapper). This is a natural place to add the updateFrequency for each Chainlink feed. The CurrencyInfo and PriceOracleInfo structs should be extended such that they can store the updateFrequency for each Chainlink feed.
