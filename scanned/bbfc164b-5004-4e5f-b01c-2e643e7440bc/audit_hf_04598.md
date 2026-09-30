# [M] M-32 | Incorrect Autocompounding Asset And Shares Conversions

## Summary
Severity: Medium
Contest weight: 0.1245
Dataset id: 22203
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In AutoCompoundingPodLp::withdraw(), it will convert the amount of assets to shares prior to calling _processRewardsToLp(). Then it will convert the shares back to assets. In between conversions, the _cbr() is likely to increase due to the increase in total assets that will occur when _processRewardsToLp() is called. This will lead to a larger output amount of assets than requested to be withdrawn. When AutoCompoundingPodLp::mint() is called, it will convert the amount of shares to assets. Then call _processRewardsToLp(), and proceed to convert the amount of assets back to shares. This will have the inverse effect, and provide a smaller amount of shares for the deposited user than requested. Ultimately, both of these functions will provide users with different amount of shares and assets respectively than expected.

## Recommendation
_processRewardsToLp() should be called in the beginning before any conversions.
