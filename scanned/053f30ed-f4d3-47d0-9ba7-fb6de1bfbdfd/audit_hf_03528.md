# [M] MKTA-1 | performUpkeep Can Be Used To Execute Any orderType

## Summary
Severity: Medium
Contest weight: 0.0682
Dataset id: 19263
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Using the performUpkeep function, the Chainlink keeper may execute any order, even if the order is not a MarketIncrease, MarketDecrease, or MarketSwap. However the MarketAutomation contract is explicitly designed to execute only market orders, therefore the scope of which orders can be executed with the performUpkeep function should be limited by validating the orderType from the dataStore.

## Recommendation
Validate that the order being executed is indeed a MarketIncrease, MarketDecrease, or MarketSwap.
