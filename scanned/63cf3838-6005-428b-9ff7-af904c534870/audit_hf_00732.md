# [M] M-18 | Utilization Fees Are Not Accurate To Liquidity Updates

## Summary
Severity: Medium
Contest weight: 0.1559
Dataset id: 2283
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The utilization fees in the BFP market are dependent on the amount of credit capacity delegated to the market by the V3 core system, however the utilization rate does not update when the amount of backing liquidity changes.
For instance, a delegator can undelegate from a vault which provides credit capacity to the BFP market and increase the utilization ratio. However this utilization update is not reflected in the utilization rate until a recomputeUtilization is triggered on the BFP side.
Therefore the utilization fees that are charged can be misrepresentative of the actual amount of liquidity utilized during these periods before a utilization recompilation is triggered.
A malicious LP could abuse this by minting sUSD directly before a utilization update in the BFP market, this way increasing the utilization ratio and forcing the the utilization fees for all traders to be higher over the next period. The LP may then backrun the utilization update and burn their sUSD that was minted.

## Recommendation
Consider implementing callbacks for markets, whereby they can update crucial pieces of their state based upon credit capacity changes which occur through the V3 system.
Otherwise implement more restrictions to the mintUsd functionality such that LPs cannot extract more value from traders than they ought to.
