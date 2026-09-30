# [H] H-18 | feeRecipient Set To Zero Blocks Functionality

## Summary
Severity: High
Contest weight: 0.1800
Dataset id: 2533
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The feeRecipient is initially set during the deployment of a SuperPool and can also be changed using the setFeeRecipient function in the SuperPool contract. This address receives fees when interest is accrued, which are minted as SuperPool shares to the feeRecipient.
The issue is that there is no restriction on the address to which the feeRecipient can be set. As a result, a SuperPool owner could inadvertently or maliciously set the feeRecipient to the zero address.
This will cause the accrue function, which is called in most operations, to revert, as the SuperPool _mint function will revert when the recipient address is zero.

## Recommendation
To prevent this issue, add a validation check in the deploySuperPool and setFeeRecipient functions to ensure that the feeRecipient address is not set to the zero address when the fee is greater than zero.
