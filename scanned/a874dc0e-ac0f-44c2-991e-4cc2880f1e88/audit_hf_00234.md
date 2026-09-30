# [M] Frontrunning `PublicLock.initialize

## Summary
Severity: Medium
Contest weight: 0.1547
Dataset id: 1203
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The unlock protocols base contract `Unlock.sol` uses `setLocktemplate()` to initialize the implementation contract for the `PublicLock` proxy. This function will initialize the relevant `PublicLock` contract which has been deployed separately. `PublicLock.initialize()` does not have any relevant access control and does not prevent arbitrary users from initialising. This means that a malicious user could front run the `setLocktemplate()` forcing the deployer of `PublicLock`’s implementation to redeploy. The process can be repeated, which costs the malicious user less than it would the owner of the Unlock Protocol, potentially unnecessarily draining funds from the development team.

## Proof of Concept
[Lack of access control on initialize](https://github.com/code-423n4/2021-11-unlock/blob/ec41eada1dd116bcccc5603ce342257584bec783/smart-contracts/contracts/PublicLock.sol#L42-L51)

## Recommendation
Implement valid access control on the `PublicLock` contract to ensure only the relevant deployer can `initialize()`.

**[julien51 (Unlock Protocol) disagreed with severity](https://github.com/code-423n4/2021-11-unlock-findings/issues/132)**

I agree with the warden, `_publicLockAddress` is deployed separately and hence `initialize` can be called before `setLockTemplate` is called.
