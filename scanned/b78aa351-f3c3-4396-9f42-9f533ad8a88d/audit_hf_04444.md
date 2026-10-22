# [M] `WithdrawalPool::withdrawalBatches` array is only every increasing in size potentially leading to Denial Of Service

## Summary
Severity: Medium
Contest weight: 0.0906
Dataset id: 21935
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
** Every time withdrawals are finalized, a new batchId gets appended to `withdrawalBatches` array. Over time, this array is ever increasing and can lead to extremely large size. It is important to note that users can trigger a queuing of withdrawal by themselves.

** Potential denial of service of `getBatchIds` and `getFinalizedWithdrawalIdsByOwner`

## Recommendation
** If `indexOfLastWithdrawal` for a batch is less than the ID of the first queued withdrawal (queuedWithdrawals[0]), it means all withdrawals in that batch and any preceding batches have been fully processed. This can be used to calculate a cut-off batch `id` on a periodic basis.

Consider the following implementation
- Find the cutoff batch: Iterate through withdrawalBatches from the beginning until you find the last batch where indexOfLastWithdrawal < queuedWithdrawals[0].
- Delete or archive: All batches up to and including this cutoff batch can be safely deleted or archived.
