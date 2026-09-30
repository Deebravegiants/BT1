# [M] Incorrect Update of Auction List after Liquidation

## Summary
Severity: Medium
Contest weight: 0.1264
Dataset id: 9802
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When liquidating a position, the removeWhenDone variable indicates whether the position should be removed from the auction list after the current liquidation. According to the comment: The auction needs to be removed if there will be no loans left when the liquidation is complete. Based on this comment, the comparison at L690 should be == nil instead. It is because if the position has no action loan after the liquidation, the util.find() function would return a nil. However, instead of checking if the position has an active loan, a more accurate way is to check if the position would become healthy after liquidation. The position should be kept on the auction list if it is still unhealthy. Otherwise, it should be removed. The current method would still keep a healthy position with an active loan on the auction list.

## Recommendation
Consider fixing the comparison at L690 or implementing the logic based on whether the position would become healthy.
