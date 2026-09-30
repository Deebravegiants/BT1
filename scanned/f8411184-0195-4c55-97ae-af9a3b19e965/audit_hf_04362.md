# [C] C-05 | Stepwise Jump In User Pending Valor

## Summary
Severity: Critical
Contest weight: 0.1433
Dataset id: 21567
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
User's pending valor is calculated based on the current accrued valor share, user's staked balance and claimed valor. The accrued valor share uses valorPerSecond and elapsed time to calculate these shares. The issue relies on the admin being able to update this valorPerSecond state variable, using the permissioned setValorPerSecond, without realizing the accumulated valor with the old rate. Any rate hike or decrease will directly affect user's claimable valor (positively or negatively).

## Recommendation
Consider moving the setValorPerSecond function to the Staking.sol contract and call updateValorVars before the rate change.
