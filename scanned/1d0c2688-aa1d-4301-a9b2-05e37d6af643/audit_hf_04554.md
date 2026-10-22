# [C] C-12 | pTKN Share Siphoning Via FlashMint

## Summary
Severity: Critical
Contest weight: 0.1458
Dataset id: 22157
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a smart contract has IFlashLoanRecipient::callback() or a fallback() function, a malicious user can set them as the receiver of the flashMint() function. This will burn .1% of their pTKN balance. Since the only restriction on the amount of pTKNs minted is that the total supply does not overflow, this can allow a user to burn the entirety of the contract's pTKN balance. This is profitable for the malicious user because burning pTKNs increases the value of existing pTKNs since they are now backed by more underlying tokens.

## Recommendation
Charge the fee to the msg.sender instead of the _recipient.
