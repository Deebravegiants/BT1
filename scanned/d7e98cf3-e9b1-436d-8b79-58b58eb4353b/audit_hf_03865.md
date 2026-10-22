# [M] Chainlink.latestRoundData() may return stale

## Summary
Severity: Medium
Contest weight: 0.3854
Dataset id: 20132
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Oracle.getUnderlyingPrice() function is used to get the price of tokens, the problem is that the function does not check for stale results.
The Oracle.getUnderlyingPrice() function is used in InsuranceFund, MarginAccount and AMM contracts. The Oracle.getUnderlyingPrice() helps to determine the tokens prices managed in the contracts.
The problem is that there is not check for stale data. There are some reasons that the price feed can become stale.
Since the token prices are used in many contracts, stale data could be catastrophic for the project.

## Recommendation
Read the updatedAt return value from the Chainlink.latestRoundData() function and verify that is not older than specific time tolerance.
```solidity
require(block.timestamp - udpatedData < toleranceTime, "stale price");
```
