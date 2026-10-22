# [M] FlashRolloverLoan_G5 will fail for

## Summary
Severity: Medium
Contest weight: 0.1192
Dataset id: 22742
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
FlashRolloverLoan_G5 calls SmartCommitmentForwarder::acceptCommitmentWithRecipient(), which will have CollateralManager committing tokens from FlashRolloverLoan_G5, which will revert as it does not approve it nor have the funds. The issue lies in the fact that FlashRolloverLoan_G5 assumes SmartCommitmentForwarder gets the borrower from the last 20 bytes, but it sets the borrower to msg.sender instead. Thus, in SmartCommitmentForwarder::acceptCommitmentWithRecipient(), TellerV2::submitBid() is called with the borrower being FlashRolloverLoan_G5, which will end up having the CollateralManager pulling collateral from FlashRolloverLoan_G5, which will fail, as it does not deal with this. FlashRolloverLoan_G5 will never work for LenderCommitmentGroup_Smart loans.

## Recommendation
In FlashRolloverLoan_G5::_acceptCommitment() pull the collateral from the borrower and approve the CollateralManager.
