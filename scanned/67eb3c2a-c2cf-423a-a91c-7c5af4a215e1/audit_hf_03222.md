# [M] Use safeTransferFrom() instead of transfer-

## Summary
Severity: Medium
Contest weight: 0.1193
Dataset id: 17836
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ERC20.transfer() and ERC20.transferFrom() functions return a boolean value indicating success. This parameter needs to be checked for success. Some tokens do not revert if the transfer failed but return false instead. Some tokens (like USDT) don't correctly implement the EIP20 standard and their transfer/transferFrom function return void instead of a success boolean. Calling these functions with the correct EIP20 function signatures will always revert. Tokens that don't actually perform the transfer and return false are still counted as a correct transfer and tokens that don't correctly implement the latest EIP20 spec, like USDT, will be unusable in the protocol as they revert the transaction because of the missing return value.

## Recommendation
Recommend using OpenZeppelin's SafeERC20 versions with the safeTransfer and safeTransferFrom functions that handle the return value check as well as non-standard-compliant tokens.
