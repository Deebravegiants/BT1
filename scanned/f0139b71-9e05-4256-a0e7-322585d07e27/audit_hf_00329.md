# [M] `_getCreatorPaymentInfo

## Summary
Severity: Medium
Contest weight: 0.1529
Dataset id: 1603
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `_getCreatorPaymentInfo()` function is utilised by `_distributeFunds()` whenever an NFT sale is made. The function uses `try` and `catch` statements to handle bad API endpoints. As such, a revert in this function would lead to NFTs that are locked in the contract. Some API endpoints receive an array of recipient addresses which are iterated over. If for whatever reason the function reverts inside of a `try` statement, the revert is actually not handled and it will not fall through to the empty `catch` statement.

## Proof of Concept
The end result is that valid and honest NFT contracts may revert if the call runs out of gas due to an unbounded `_recipients` array. `try` statements are only able to handle external calls.

## Recommendation
Consider bounding the number of iterations to `MAX_ROYALTY_RECIPIENTS_INDEX` as this is already enforced by `_distributeFunds()`. It may be useful to identify other areas where the `try` statement will not handle reverts on internal calls.
Yes - this code is trying to be very defensive so that NFTs cannot get stuck in escrow. This is a great suggestion on how we could continue to improve.

Instead of capping the loop lengths in `_getCreatorPaymentInfo` we have opted to remove them entirely. There was another simplification that happened recently to this function that made removal a viable option. Now the only other loop for this data is in _distributeFunds and we already cap the max length there.
