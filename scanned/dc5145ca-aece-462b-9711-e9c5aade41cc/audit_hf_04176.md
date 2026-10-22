# [M] M-04 | Blast Point Remunerations May Be Gamed

## Summary
Severity: Medium
Contest weight: 0.1229
Dataset id: 20857
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the BlastOnboarding contract users may deposit their token balances and will be remunerated with the points they would have otherwise received if they didn't deposit into the contract. These point remunerations will occur off-chain at undisclosed times. However if a user is able to predict, recognize a pattern, or guess within a reasonable range when the distributions will occur they could deposit before the distribution and withdraw after the distribution to receive more Blast Points than they otherwise would have by simply depositing into the BlastOnboarding contract for the entire period or simply holding the native yield tokens for the entire period. The same may occur with a malicious Liquidity Provider for the MagicLP contract.

## Recommendation
In the case of the BlastOnboarding contract, consider requiring that users have locked amounts to reward them with point distributions. Otherwise ensure there is no way for users to predict when the off-chain point remuneration will occur.
