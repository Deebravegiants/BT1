# [C] C-01 | Removed Request Is Always The Last

## Summary
Severity: Critical
Contest weight: 0.2620
Dataset id: 21584
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[Vesting._cancelVestingRequest()](https://github.com/GuardianAudits/omnichain-ledger-1/blob/d68be172d909441ee31674a6b3cd26b143adc8bd/contracts/lib/Vesting.sol#L145) and [Vesting._claimVestingRequest](https://github.com/GuardianAudits/omnichain-ledger-1/blob/d68be172d909441ee31674a6b3cd26b143adc8bd/contracts/lib/Vesting.sol#L193) try to remove the current request by:
1. Overriding it in the storage with the last request in the array.
2. Deleting the last request. It fails to execute the first step because it only updates the local variable to point to the last request, but no real storage update is done. As result, the removed request is always the last one. A malicious user can use that to create a cancel request with large value followed by many 1-wei cancel requests. They can then cancel their large request many times because on each cancel, one of the 1-wei requests will be removed instead of the real one. This will cause the user's staked balance to grow indefinitely and result in stolen funds.

## Proof of Concept
https://github.com/GuardianAudits/omnichain-ledger-1/pull/2/files

## Recommendation
Do not assign values from storage to storage just before deleting them. Cache the value to move to memory, assign it to its new index, and then pop the last element from the storage.
