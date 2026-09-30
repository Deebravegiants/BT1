# [M] Setting maxFundingFeePerBlock to a lower value than abs(lastFundingRate) will brick getPendingAccFundingFees()

## Summary
Severity: Medium
Contest weight: 0.0701
Dataset id: 11144
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
getPendingAccFundingFees() computes the number of blocks to the limit by subtracting absLastFundingRate to maxFundingFeePerBlock.
setMaxFundingFeePerBlock() allows setting the max to any value below MAX_FUNDING_FEE.
If maxFundingFeePerBlock is set to a value smaller than absLastFundingRate it will underflow, bricking getPendingAccFundingFees() and it can only be fixed by calling setPairFundingFees().

## Recommendation
Revert if setMaxFundingFeePerBlock() is called with maxFundingFeePerBlock smaller than absLastFundingRate.
