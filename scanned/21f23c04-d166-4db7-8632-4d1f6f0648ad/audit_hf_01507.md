# [M] M-21 Incorrect work with decimals

## Summary
Severity: Medium
Contest weight: 0.0931
Dataset id: 8000
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DistributionEvent.totalTournamentEarnings and DistributionEvent.totalOtherEarnings are stored for the current token's decimals (FantiumClaimingV1.sol#L63). If the new token is set with an other number of decimals after the distribution is created, these variables will contain incorrect values. Therefore, DistributionEvent.tournamentDistributionAmount and DistributionEvent.otherDistributionAmount will contain incorrect values as well (FantiumClaimingV1.sol#L698). This will lead to an incorrect amount of distributed funds.

## Recommendation
We recommend storing totalTournamentEarnings and totalOtherEarnings without decimals. In such cases amountPaidIn, tournamentDistributionAmount, and otherDistributionAmount should be stored without decimals too.
