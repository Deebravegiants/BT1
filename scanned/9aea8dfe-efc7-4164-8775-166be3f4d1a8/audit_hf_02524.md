# [H] Wrong LP price calculated

## Summary
Severity: High
Contest weight: 0.0990
Dataset id: 13483
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`TotalSupply` amount is read directly from storage. 

Attacker can manipulate that amount using a flash loan and change the calculated LP token price. This is also an issue during regular calculation because the TVL is calculated based on time-averaged values but total supply is a current block value which will result consistently incorrect results.

## Recommendation
No recommendation
