# [M] Claim Collateral on Behalf of HAs

## Summary
Severity: Medium
Contest weight: 0.1327
Dataset id: 14165
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a collateral pool is being revoked users are able to make claims over the collateral. These claims are paid out based on preference. Users are able to attach governance tokens to their claims to give the claims a higher preference.  
In CollateralSettlerERC20, the function claimHA() may be called by any user and will make a claim for the perpetual owner. As part of this function, the user is able to specify how much governance tokens are to be attached. Since there are no requirements for who the message sender is when claiming a perpetual, a malicious user may claim other users perpetuals with zero governance tokens attached.  
The benefit of this attack is that the malicious user would have a higher priority when it comes to redeeming the tokens if they have attached governance tokens when claiming their perpetual.

## Recommendation
Consider only allowing users who are either approved or the owner of a perpetual to be allowed to claim a perpetual. This can be achieved through a public getter of the function PerpetualManagerInternal._isApprovedOrOwner().
