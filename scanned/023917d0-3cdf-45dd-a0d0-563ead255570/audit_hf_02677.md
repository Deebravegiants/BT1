# [M] Double Use Of Validator Public Key Can Re-introduce Security Issues

## Summary
Severity: Medium
Contest weight: 0.1994
Dataset id: 14470
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The OperatorDelegator contract was updated since our original review to include a mapping of validatorCurrentStakedButNotVerifiedEth. This change was made to protect against various accounting discrepancies, see RENZO-09. However, reusing the same public key across different OperatorDelegator contracts will cause regression issues, introducing all the same accounting discrepancies.

The stakeEth tracks validatorCurrentStakedButNotVerifiedEth as a mapping of validatorPubKeyHash to non-verified eth. This mapping is not checked elsewhere in other contracts. Since the relationship between RestakeManager to OperatorDelegator is one to many, it is possible to have multiple OperatorDelegator contracts all containing their own validatorCurrentStakedButNotVerifiedEth. Since no reconciliation is done across the different OperatorDelegator contracts, it is possible to reuse the same public key across different instances of OperatorDelegator contracts.

Reuse of the same public key, will reintroduce the following issues;
1. RENZO-02
2. Double stake then verify overinflates TVL, see RENZO-09
3. An additional issue involving staking, verifying withdrawal credentials, then staking again inflating TVL. This was not identified in the original issue RENZO-09 but has the same impact. It is worth mentioning that this issue exists across individual instances of the OperatorDelegator contract as well.

## Recommendation
The testing team recommends keeping a global registry of all public keys in use to insure the same key isn’t used twice. Additionally, it is worth considering the solution provided in Resolution which would prevent the funds being trapped in withdrawal credentials that are potentially not accurate for that OperatorDelegator.
