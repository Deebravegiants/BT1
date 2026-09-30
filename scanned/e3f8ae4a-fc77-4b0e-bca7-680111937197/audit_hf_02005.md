# [M] Reduce impact of emergencyUpdatequestPeriod()

## Summary
Severity: Medium
Contest weight: 0.1903
Dataset id: 11326
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function emergencyUpdatequestPeriod() allows the merkle tree to be updated. The merkle tree contains an embedded index parameter which is used to prevent double claims. When the merkleRoot is updated, the layout of indexes in the merkle tree could become different. Example: Suppose the initial merkle tree contains information for:
- user A: index=1, account = 0x1234, amount=100
- user B: index=2, account = 0x5689, amount=200
Then user A claims => _setClaimed(..., 1) is set. Now it turns out a mistake is made with the merkle tree, and it should contain:
- user B: index=1, account = 0x5689, amount=200
- user C: index=2, account = 0xabcd, amount=300
Now user B will not be able to claim because bit 1 has already been set. Under this situation the following issues can occur:
• Someone who has already claimed might be able to claim again.
• Someone who has already claimed has too much.
• Someone who has already claimed has too little, and cannot longer claim the rest because _setClaimed() has already been set.
• someone who has not yet claimed might not be able to claim because _setClaimed() has already been set by another user.

## Recommendation
The following steps can be taken to reduce the impact:
• Only allow an update if no claims have been done yet, by checking no bits have been set yet. However this has limited use.
• Make sure the index number of a user always stays the same, although this doesn’t help if the user is entitled to an higher amount.
• Exclude already claimed tokens from the new merkle tree. To prevent claiming in the mean time, it might be a good idea to pause the claiming to make sure no claims are done in the mean time. Reset all the bits after the update.
• Consider storing how much each account has claimed and allow the account to claim less on future claims, in case the account has claimed too much. However this requires some complicated logic.
