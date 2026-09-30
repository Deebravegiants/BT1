# [M] MKTU-4 | Unwieldy Claimable Collateral Controls

## Summary
Severity: Medium
Contest weight: 0.1696
Dataset id: 18888
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the claimCollateral function the claimableFactor is the maximum of the claimableFactorForTime and claimableFactorForAccount. Therefore in the case where capped negative price impact is manipulated and claimable collateral ought to be used at the protocol's discretion to punish the manipulator, the controls will be insuﬃcient. Consider the following: A malicious trader manipulates reference prices to take advantage of negative PI capping. Many other traders are capped in the same timekey as this one malicious trader. The other traders ought to be able to claim their collateral at a later date, but the malicious trader should never have their claimableFactor updated. The current controls are not well suited for this scenario since every non-malicious trader would have to have a manual per-account claimableFactorForAccount conﬁgured. In the case where there are many innocent traders in this timekey this may be impractical, especially in times of market volatility. The controls should be ﬂipped such that the single malicious trader can be punished with a more constrictive claimableFactorForAccount.

## Recommendation
Alter the claimableFactorForAccount logic such that it is a more constrictive threshold rather than a less constrictive one. This would likely be accompanied by a isClaimableFactorForAccountEnabled boolean value to indicate whether the claimableFactorForAccount ought to be used in the case that it is the default value of zero.
