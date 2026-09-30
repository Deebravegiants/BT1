# [H] ORDH-1 | Unaccounted Gas Expenditure When Setting Prices

## Summary
Severity: High
Contest weight: 0.1401
Dataset id: 18170
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The startingGas variable is declared inside of the executeOrder function. As a result, it will be the amount of gas left after the setting of prices, which is particularly gas intensive. When calculating how much gas was used in GasUtils.payExecutionFee, keepers won't be remunerated for this expenditure which will run a significant deficit over time.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/ORDH-1.ts

## Recommendation
Refactor the way gas expenditure is tracked so that the gas used for the withOraclePrices modifier is included in the keeper’s remuneration.
