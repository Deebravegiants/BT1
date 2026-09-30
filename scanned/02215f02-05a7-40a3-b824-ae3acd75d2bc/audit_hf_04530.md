# [M] M-11 | Interest Rates Not Accurate To Liquidity Updates

## Summary
Severity: Medium
Contest weight: 0.1481
Dataset id: 22094
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The utilization fees in the Perps-V3 market are dependent on the amount of credit capacity
delegated to the market by the V3 core system, however the utilization rate does not update when
the amount of backing liquidity changes.
For instance, a delegator can undelegate from a vault which provides credit capacity to the Perps-V3
market and increase the utilization ratio. However this utilization update is not reflected in the
utilization rate until a updateInterestRate is triggered on the Perps-V3 side.
Therefore the interest rate that is charged can be misrepresentative of the actual amount of liquidity
utilized during these periods before an interest rate update is triggered.
A malicious LP could abuse this by minting sUSD directly before a interest rate update in the
Perps-V3 market, this way increasing the utilization ratio and forcing the the interest rate for all
traders to be higher over the next period.
The LP may then backrun the interest rate update and burn their sUSD that was minted.

## Recommendation
Consider calling GlobalPerpsMarketModule.updateInterestRate each time backing liquidity in the V3
core system changes.
