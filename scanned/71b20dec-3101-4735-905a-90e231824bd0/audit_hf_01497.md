# [H] H-13 An incorrect check

## Summary
Severity: High
Contest weight: 0.1631
Dataset id: 7943
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is an incorrect check in the updateDistribtionTotalEarningsAmounts() function
FantiumClaimingV1.sol#L326-L327. Instead of a check for _totalTournamentEarnings and
_totalOtherEarnings there should be a check for tournamentDistributionAmount and
otherDistributionAmount after calling the triggerClaimingSnapshot function. Otherwise, the
manager could reduce tournamentDistributionAmount and otherDistributionAmount by
mistake and block the distribution (the athlete will not be able to add tokens and will also close the
distribution).

## Recommendation
We recommend adding a check for tournamentDistributionAmount and
otherDistributionAmount after calling the triggerClaimingSnapshot function. Also, the same
check should be added to the updateDistributionEventCollectionIds function.
