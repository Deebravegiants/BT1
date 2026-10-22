# [M] Allocation can start before registra-

## Summary
Severity: Medium
Contest weight: 0.5752
Dataset id: 20460
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The way that timestamps are set or specifically, validated right now allows Allocation to start before Registration ends. I havent git a clear answer from the this can potentially break some stuff in QVBaseStrategy and DonationVotingMerkleDistributionBaseStrategy.
If _registerRecipient is called while Allocation is active on both QVBaseStrategy and DonationVotingMerkleDistributionBaseStrategy This can completely modify the effects of reviewRecipients and rewrite the status of already 'reviewed' recipients. This can cause rewards being falsely distributed or even stuck as well.
Of course there is a check to see if the caller is a member of the pool. Since the members are 'trusted' then the likelihood is low, thus the impact will be medium, if those roles are not to be trusted, then impact can potentially be high.
Recipient statuses can be modified and altered causing funds to sent falsely or get stuck.
This is the check to validate timestamps in both strategies. As we can see, it allows allocationStartTime to be less than registrationEndTime.
```solidity
if (
    block.timestamp > _registrationStartTime || _registrationStartTime > _registrationEndTime
    || _registrationStartTime > _allocationStartTime || _allocationStartTime > _allocationEndTime
    || _registrationEndTime > _allocationEndTime
) revert INVALID();
```

## Recommendation
Consider adding check to revert if allocation can start before registration ends:
```solidity
if (
    block.timestamp > _registrationStartTime || _registrationStartTime > _registrationEndTime
    || _registrationStartTime > _allocationStartTime || _allocationStartTime > _allocationEndTime
    || _registrationEndTime > _allocationEndTime
    || _registrationEndTime > _allocationStartTime
) {
    revert INVALID();
}
```
