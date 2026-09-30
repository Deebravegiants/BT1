# [M] M-06 | Block Stuﬃng Risk

## Summary
Severity: Medium
Contest weight: 0.0939
Dataset id: 20846
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the block.timestamp is a few seconds before the beginning of a new hour and User A sends a tx to pay back their full loan amount, the lender may stuff blocks on the network until the next hour begins. As a result, the borrowers debt to be repaid will increase and the borrowers tx will no longer close the loan. Immediately the borrower will have to pay an additional period of interest. More insidiously, the borrower may not realize that the loan remains open and as a result may be unexpectedly liquidated.

## Recommendation
Consider allowing users to pass a boolean indicating whether they would like to repay the full amount, rather than always specifying a particular amount to pay back. This way the transaction will close the loan regardless of when the transaction is recorded.
