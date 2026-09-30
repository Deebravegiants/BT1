# [M] M-20 | Chainlink Oracles Lack Proper Validation

## Summary
Severity: Medium
Contest weight: 0.0873
Dataset id: 2554
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _getPriceWithSanityChecks function is used in the ChainlinkEthOracle and ChainlinkUsdOracle contracts to validate the fetched price updates from the Chainlink feed. However, in the current implementation, the validation only reverts when the price is less than zero, meaning a price of zero would be considered valid. This price is used to calculate position values and determine if positions can be liquidated. Consequently, positions could be incorrectly liquidated if a price of zero is returned instead of the oracle reverting.

## Recommendation
Modify the price check to revert if the returned price is less than or equal to zero.
