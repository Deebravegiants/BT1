# [H] H-04 | Stepwise Jump From Claimable Funds Omitted

## Summary
Severity: High
Contest weight: 0.2252
Dataset id: 2035
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The positionMargin function fails to include claimable funding fees and claimable collateral. This omission creates opportunities for users to steal yield by timing their deposits before fee claims. The vulnerability exists because when these fees/rewards are later claimed, they cause a step increase in the vault's total value, which directly impacts the PPS (Price Per Share). This creates an exploitable scenario where users can: 1. Monitor positions for unclaimed fees/collateral 2. Deposit into the vault right before claims are processed 3. Capture a portion of the yield they didn't help generate 4. Exit with profits taken from legitimate long-term holders The impact is severe because: • Multiple claimable types are affected (funding, collateral) • Claims/Keepers are predictable • The attack requires no special permissions • Profit potential scales with unclaimed amounts

## Recommendation
Modify positionMargin to include both claimable funding fees and claimable collateral. These would be claimed with claimFundingFees and claimCollateral in the GMX ExchangeRouter respectively.
