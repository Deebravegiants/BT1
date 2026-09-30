# [H] MKTU-6 | Rounding Error Causes Market Insolvency

## Summary
Severity: High
Contest weight: 0.3071
Dataset id: 18200
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the per-size values are computed, for tokens such as USDC with only 6 decimals of precision and large open interest values, there can be rounding error due to the division that occurs in toFactor. For example: 1. $10,000,000 of open interest will have a total number of 38 digits. 2. 1 USDC will have a total number of 37 digits after multiplying by FLOAT_PRECISION. 3. Therefore when calculating the per-size values, precision loss on the order of <10 USDC can occur due to truncation. Additionally, when calculating the per-size values, the resulting values are often not exact multiples of each other. For example: 1. Open Interest is $10,000 short and $20,000 long both with the long token as collateral. 2. Assume cache.fundingUsdForShortCollateral / prices.shortTokenPrice.max yields 57600399999999999. 3. 57600399999999999 / 10,000 = 5760039999999 will be the short funding factor magnitude. 4. 57600399999999999 / 20,000 = 2880019999999 will be the long funding factor. 5. However 2880019999999 / 5760039999999 = ~0.49999999999991 != 0.5. This can result in less funding fees being paid than collected. Such a deficit will eat into the balance of the market and potentially prevent LPers from withdrawing their entire deposits or prevent traders from claiming their funding fees.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/MKTU_6.ts

## Recommendation
Avoid this precision loss for low precision tokens so that the same amount of funding fees are paid as collected. Address the precision lost when the resulting per-size values are not exact multiples.
