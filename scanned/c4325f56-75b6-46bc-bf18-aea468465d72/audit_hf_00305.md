# [M] Name squatting

## Summary
Severity: Medium
Contest weight: 0.1160
Dataset id: 1527
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[LensHub.sol#L142](https://github.com/code-423n4/2022-02-aave-lens/blob/aaf6c116345f3647e11a35010f28e3b90e7b4862/contracts/core/LensHub.sol#L142)  

Creating profiles through `LensHub/PublishingLogic.createProfile` does not cost anything and will therefore result in “name squatting”.  
A whitelisted profile creator will create many handles that are in demand, even if they don’t need them, just to flip them for a profit later.  
This ruins the experience for many high-profile users that can’t get their desired handle.

## Recommendation
Consider auctioning off handles to the highest bidder or at least taking a fee such that the cost of name squatting is not zero.

Declined. This is by design. Governance can allow contracts/addresses to mint. If governance allows a malicious actor that is the fault of governance. Governance can also allow contracts that implement auction or other functionality as well to manage the profile minting system.
The protocol should take no opinion on this by default.

I will mark this as `medium` risk for the same reasons outlined in [M-03 (Issue #26)](https://github.com/code-423n4/2022-02-aave-lens-findings/issues/26#issuecomment-1125814379).
