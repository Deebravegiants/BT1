# [C] MKTU-2 | Funding Fees Partially Paid

## Summary
Severity: Critical
Contest weight: 0.2761
Dataset id: 18155
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getNextFundingAmountPerSize function, the fundingAmountPerSizePortion values are calculated by dividing the corresponding fundingUsd by the open interest of both longs and shorts. This is done to get a value that is to be received/paid for each collateral type for each position direction. This logic makes sense in the case where users are being paid the funding fees since they are able to claim both the long and short tokens. However users are only able to pay the fundingAmountPerSizePortion value for their respective collateral token. This errantly reduces the amount the fundingAmountPerSizePortion that is paid for each corresponding collateral token as the amounts are divided by the entire open interest of the side that is paying funding fees. As a result, only a portion of the funding fees are being paid while the entire amount can be claimed, and a deficit in the pool accounting is created which will force markets into insolvency over time.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/MKTU_2.ts

## Recommendation
Implement separate logic for the side that is paying the funding fees where the funding fees are not spread across the entirety of the open interest for that side, but rather the open interest of that side that is able to pay the particular token through their collateral. E.g. cache.fps.fundingAmountPerSizePortion_LongCollateral_LongPosition = getPerSizeValue(cache.fundingUsdForLongCollateral / prices.longTokenPrice.max, cache.oi.longOpenInterestWithLongCollateral);
