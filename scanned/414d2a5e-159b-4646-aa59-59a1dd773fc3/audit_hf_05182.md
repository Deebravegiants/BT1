# [M] FTokens are burned after quor

## Summary
Severity: Medium
Contest weight: 0.4318
Dataset id: 23251
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
params.quorumVotes is larger than it should because Locker's collection tokens are burned after quorumVotes is recorded.
```solidity
uint newQuorum = params.collectionToken.totalSupply() * SHUTDOWN_QUORUM_PERCENT / ONE_HUNDRED_PERCENT;
if (params.quorumVotes != newQuorum) {
    params.quorumVotes = uint88(newQuorum);
}
// Lockdown the collection to prevent any new interaction
// `totalSupply`. If this was called before
// `params.quorumVotes` was set, the totalSupply() would be smaller and each vote would get more share of the ETH profits.
locker.sunsetCollection(_collection);
```
When a collection is shut down, its NFTs are sold off via Dutch auction in a SudoSwap pool. This sale's ETH profits are distributed to the holders of the collection token (fToken). The claim amount is calculated with availableClaim*claimableVotes/params.quorumVotes*2. The higher params.quorumVotes, the lower the claim amount for each vote. params.quorumVotes is larger than it should because Locker's collection tokens are burned after quorumVotes is recorded. Internal pre-conditions 1. At least 50% of Holders have voted for a collection to shut down. 2. No listings for the target collection exist. External pre-conditions None Attack Path 1. Admin calls . The vulnerability always happens when this is called. A portion of the claimable ETH can never be claimed and all voters can claim less ETH.

## Recommendation
Consider calling Locker::sunsetCollection() before setting the params.quorumVotes in . Disclaimers project. Usage of all smart contract software is at the respective users’ sole risk and is the users’ responsibility.
