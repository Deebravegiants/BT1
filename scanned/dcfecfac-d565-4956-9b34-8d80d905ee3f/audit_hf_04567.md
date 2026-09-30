# [H] H-12 | Lack Of _selfLendingPairPod Validation

## Summary
Severity: High
Contest weight: 0.1826
Dataset id: 22170
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calling addLeverage(), a user is allowed to input whatever _selfLendingPairPod they desire, without any validation. This will allow a user to successfully add leverage with a self lending pod that is different from the pod they used to create their position. However when they attempt to withdraw, they will be forced to use the pod associated with their NFT. This will prevent a user from removing leverage on their position, and force the position to be open indefinitely. Since positions are transferable, a malicious user could sell their position to an unsuspecting user. This will lead to a user being stuck with a worthless position.

## Recommendation
Validate that the _selfLendingPairPod passed in to addLeverage() is the same pod associated with their NFT. Alternatively, allow users to update the selfLendingPod they have associated with their position NFT.
