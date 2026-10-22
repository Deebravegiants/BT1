# [H] H-10 | Price Impact Cap On DecreasePosition

## Summary
Severity: High
Contest weight: 0.1683
Dataset id: 21968
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GMX can cap negative price impact on decrease orders, leaving the excess amount in a claimable collateral pool that must be manually claimed using the ExchangeRouter.claimCollateral function. This scenario is not currently handled, meaning that if it occurs during a user withdrawal, the user could receive less than they should have. Additionally, the GmxUtils contract does not currently implement the claimCollateral function, which means those funds cannot be retrieved, leading to potential losses for users.

## Recommendation
Update the GmxUtils contract to implement the claimCollateral function, ensuring that any excess funds due to capped negative price impact can be claimed and properly accounted for. Additionally, modify the withdrawal process to handle this scenario, ensuring users receive the full amount they are entitled to, even when negative price impact is capped.
