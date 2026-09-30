# [M] DATA-1 | OI Validation Leads To Skew

## Summary
Severity: Medium
Contest weight: 0.3794
Dataset id: 20551
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The validation to ensure the maximum open interest is not exceeded compares both trading sides in aggregate:
```solidity
if (config.totalLongs + config.totalShorts > (2 * config.maximumOi)) revert LibError.MaxOI();
```
With the current open interest (OI) validation, longs are able to dictate how much in shorts can be opened and vice versa. For example, if traders establish 1800 ETH in long OI, only 200 ETH in short OI can be opened when the maximumOi is set to 1000 ETH. This inherently leads the market to be imbalanced.

## Recommendation
Validate open interest per side rather than in aggregate.
