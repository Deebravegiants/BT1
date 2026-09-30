# [M] [NAZ-M1] Chainlink’s `latestRoundData` Might Return Stale Results

## Summary
Severity: Medium
Contest weight: 0.3926
Dataset id: 16712
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Across these contracts, you are using Chainlink’s `latestRoundData` API, but there is only a check on `updatedAt`. This could lead to stale prices according to the Chainlink documentation:

* [Historical Price data](https://docs.chain.link/docs/historical-price-data/#historical-rounds)
* [Checking Your returned answers](https://docs.chain.link/docs/faq/#how-can-i-check-if-the-answer-to-a-round-is-being-carried-over-from-a-previous-round)

The result of `latestRoundData` API will be used across various functions, therefore, a stale price from Chainlink can lead to loss of funds to end-users.

## Recommendation
Consider adding the missing checks for stale data.

For example:

```solidity
(uint80 roundID ,answer,, uint256 timestamp, uint80 answeredInRound) = AggregatorV3Interface(chainLinkAggregatorMap[underlying]).latestRoundData();

require(answer > 0, "Chainlink price <= 0"); 
require(answeredInRound >= roundID, "Stale price");
require(timestamp != 0, "Round not complete");
```

Agree. We’ll add the additional checks.
