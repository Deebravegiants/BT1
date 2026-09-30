# [M] M-04 | Liquidity Premium Rounds Down To 0

## Summary
Severity: Medium
Contest weight: 0.1128
Dataset id: 21484
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The liquidity premium is used to calculate the liquidity of the DISCOVERY range, based on the ANCHOR range liquidity, during rebalances. The main goal is to scale DISCOVERY range liquidity based on the ratio depending on the tick distance of the active tick to the floor tick, and the TICK_PREMIUM_FACTOR. The issue involves the initialized value of TICK_PREMIUM_FACTOR. There is a discrepancy between the tests and the deploy script, as the tests use 4800 but the deploy script uses 4800e18. In case the 4800e18 value is used, it will cause the getLiquidityPremium calculation round to 0, whenever the tick difference is less than 4800. During a sweep and slide this issue will make DISCOVERY liquidity equal to the ANCHOR liquidity.

## Recommendation
Be sure TICK_PREMIUM_FACTOR is initialized with the correct value of 4800.
