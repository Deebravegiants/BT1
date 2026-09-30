# [M] getClaimableAmount calls return positive amounts even if user does not have vestings

## Summary
Severity: Medium
Contest weight: 0.1097
Dataset id: 17537
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The getClaimableAmount function of all vesting contracts should return the claimable amounts of the _beneficiary parameter. They compute a hash based on the beneficiary and other parameters but it’s not checked that this hash is actually in the merkle tree. Therefore, this function also returns positive claimable amounts for users that don’t have anything to claim. It could be that third-party smart contracts rely on this function to correctly return the claimable amount that could be received through a claimTokens call, given the same parameters plus a valid merkle proof. The function also returns positive claimable amounts for users that don’t have anything to claim.

## Recommendation
Third parties should not merely rely on the return value from getClaimableAmount but also verify whether the queried user or award hash exists. Confirmed
