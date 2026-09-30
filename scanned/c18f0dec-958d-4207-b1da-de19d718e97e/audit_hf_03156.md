# [H] VaultImplementation._validateCommitment may cause DoS

## Summary
Severity: High
Contest weight: 0.2014
Dataset id: 17708
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The calculation of potentialDebt in VaultImplementation._validateCommitment() is incorrect and will cause a DoS to legitimate borrowers. The calculation of potentialDebt in VaultImplementation._validateCommitment() is incorrect because it computes uint256 potentialDebt = seniorDebt * (ld.rate + 1) * ld.duration; which incorrectly adds a factor of ld.duration to seniorDebt thus making the potential debt much higher by that factor than it will be. The use of INTEREST_DENOMINATOR and implied lien rate is also missing here. Liens that would have otherwise satisfied the constraint of potentialDebt <= ld.maxPotentialDebt will fail because of this miscalculation and will cause a DoS to legitimate borrowers and likely all of them.

## Recommendation
Change the calculation to uint256 potentialDebt = seniorDebt * (ld.rate * ld.duration + 1).mulDivDown(1, INTEREST_DENOMINATOR);. This should also consider the implied rate of all the liens against the collateral instead of only this lien.
