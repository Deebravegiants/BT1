# [M] Missing input validation

## Summary
Severity: Medium
Contest weight: 0.0832
Dataset id: 16397
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Throughout the codebase there are couple of places where important input validation is missing.
setPlatformFeePercent()
setMaxWalletLimit()
Not constraining the parameters of these functions can create problems due to an error or malicious activities from a compromised owner when calling them.
Also in listNFTForAuction() we can observe that a check for endAt param is missing. This can cause the auction to end even 1 second after the current block.timestamp or in a time far in the future.

## Recommendation
You can create a check where exampleParam should be less than x and greater than y, otherwise revert the transaction.
