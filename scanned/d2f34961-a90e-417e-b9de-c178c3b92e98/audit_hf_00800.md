# [M] M-01 | Unsafe Use Of transferFrom

## Summary
Severity: Medium
Contest weight: 0.1149
Dataset id: 2536
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Some ERC-20 tokens return a boolean instead of reverting therefore using transferFrom will not revert when the transfer fails.
This can be abused in the liquidate function as the flow looks like the following:
• The liquidator repays the debt of the borrower:
• The funds are transferred from the liquidator to the position (if the transfer fails with such a token nothing happens here)
• The debt of the borrower is reduced in the pool
• The liquidator seizes funds from the position as reward
Therefore if the transferFrom call failed without reverting the debt of the borrower is reduced but the funds in the pool stayed the same and the liquidator receives rewards from the position for free.

## Recommendation
Use safeTransferFrom instead of transferFrom.
