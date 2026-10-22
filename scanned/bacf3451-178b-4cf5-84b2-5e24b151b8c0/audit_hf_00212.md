# [M] No Transfer Ownership Pattern

## Summary
Severity: Medium
Contest weight: 0.1530
Dataset id: 1101
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current ownership transfer process involves the current owner calling `Swap.transferOwnership()`. This function checks the new owner is not the zero address and proceeds to write the new owner’s address into the owner’s state variable. If the nominated EOA account is not a valid account, it is entirely possible the owner may accidentally transfer ownership to an uncontrolled account, breaking all functions with the `onlyOwner()` modifier.

## Proof of Concept
1. Navigate to ”https://github.com/code-423n4/2021-11-bootfinance/blob/7c457b2b5ba6b2c887dafdf7428fd577e405d652/customswap/contracts/Swap.sol#L30”
2. The contract has many `onlyOwner` function.
3. The contract is inherited from the Ownable which includes `transferOwnership`.

## Recommendation
Implement zero address check and consider implementing a two step process where the owner nominates an account and the nominated account needs to call an `acceptOwnership()` function for the transfer of ownership to fully succeed. This ensures the nominated EOA account is a valid and active account.

upgrading to med severity as this could impact availability of protocol 

2 — Med: Assets not at direct risk, but the function of the protocol or its availability could be impacted, or leak value with a hypothetical attack path with stated assumptions, but external requirements.
