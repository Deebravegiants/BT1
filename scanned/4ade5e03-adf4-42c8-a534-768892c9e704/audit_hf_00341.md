# [M] Rewards can be lost

## Summary
Severity: Medium
Contest weight: 0.4221
Dataset id: 1678
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability arises from the ability of the bribeVault contract to invoke the updateRewardsMetadata function multiple times for the same rewardIdentifier while a reward distribution is still active. The function overwrites the stored merkleRoot and the associated proof data that users rely on to prove eligibility for their rewards. Because the merkle tree is recomputed and the proof for a particular user (for example, User A) is replaced when the metadata is updated, the original proof becomes invalid. Consequently, if a user has not yet called the claim function before the second update occurs, the contract will reject the claim or return zero, effectively causing the user’s allocated reward to disappear. This occurs whenever an admin or privileged account calls updateRewardsMetadata before all claimers have submitted their claims, either unintentionally due to a mistaken re‑initialisation of the merkle root or maliciously to deny payouts. The impact is a loss of expected funds for legitimate participants, a breach of the protocol’s accounting guarantees, and erosion of trust in the reward distribution mechanism. The issue was discovered during a security audit that examined the interaction between bribeVault’s admin functions and the merkle‑proof‑based claim workflow; the auditors noted that the contract does not enforce a "claim‑finished" condition before allowing metadata to be altered. Detecting this problem in production can be difficult because the front‑end may still display that a reward is allocated, yet the claim transaction silently fails, leaving users confused by a zero‑balance result without obvious error messages. The flaw belongs to the class of mutable‑state‑or‑overwrites bugs in merkle‑proof‑based reward systems, where the integrity of the proof set is assumed to be immutable for the duration of the claim period. To remediate the issue, the contract should restrict updateRewardsMetadata so that it can only be called after all entitled addresses have claimed, or it should make the merkleRoot immutable once a distribution is active, possibly by introducing a separate finalisation step or by storing claim state per user and refusing to replace proofs that would invalidate pending claims. From the user’s perspective, the symptom is that they see a reward allocated to their address but, when attempting to claim, they receive no tokens or encounter a revert, contrary to the expectation that the system will honor the announced payout. This mismatch between displayed rewards and actual claimability violates the protocol’s financial logic and can result in unrecoverable loss of funds for affected participants.

## Proof of Concept
1. bribeVault calls the updateRewardsMetadata at [RewardDistributor.sol#L97](https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/RewardDistributor.sol#L97) using rewardIdentifier X  
2. Assume _distributions[i].proof contains merkle proof for User A  
3. User A fails to call claim function  
4. bribeVault again calls the updateRewardsMetadata at RewardDistributor.sol#L97 using rewardIdentifier X updating _distributions[i].proof which might not contain merkle proof of User A now. So User A loses his rewards

## Recommendation
```solidity
bribeVault should only make second call to updateRewardsMetadata on same rewardIdentifier when all claimers have made their claims.
```

We would only call `updateRewardsMetadata` again if there was an issue with the originally-set merkle root(s). The recommended mitigation steps above would block us from setting the correct merkle roots until after claimers claimed the wrong amounts.

Thanks again for participating in our contest csanuragjain, looking forward to more feedback/suggestions/comments.

The finding highlights the consequences of admin privilege, in that the admin can use `updateRewardsMetadata` to deny claims.

While I believe the warden could have done a better job at expressing the risks involved for users, I believe the finding to be valid.
