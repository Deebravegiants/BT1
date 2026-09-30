# [M] FlashRolloverLoan_G5 will not work for certain

## Summary
Severity: Medium
Contest weight: 0.1257
Dataset id: 22743
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
FlashRolloverLoan_G5::_repayLoanFull() approves TELLER_V2 for _repayAmount, but TELLER_V2 always pulls the principal and interest, possibly leaving some dust approval left. Some tokens revert when trying to set approvals from non null to non null, which will make FlashRolloverLoan_G5 revert. Some ERC20 tokens must have 0 approval before setting an approval to a non 0 amount, such as USDC. The interest rises with block.timestamp, so borrowers will likely take a flash loan slightly bigger than _repayAmount to take this into account, or repay will fail. Thus, when the approval is set for TellerV2 of the _principalToken, principal + interest may be less than the approval, which will leave a dust approval. FlashRolloverLoan_G5::executeOperation() later on approves POOL, which will revert as a dust amount was left. FlashRolloverLoan_G5 will not work and be DoSed.

## Recommendation
Set the approval to 0 after repaying the loan.
