# [H] Incorrect Tag Parsing in Interest Sync

## Summary
Severity: High
Contest weight: 0.2880
Dataset id: 9807
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the interest.lua contract, the syncInterests function incorrectly checks for a repayment action by evaluating msg.Tags.Action == "Repay". However, according to the messaging conventions established by the protocol (specifically the borrow-loan-interest-sync-dynamic pattern), the repayment intent is signaled via the X-Action tag, not the Action tag. As a result, the intended conditional branch for interest synchronization on repayments is bypassed, and execution falls through to the default else block. This default case uses msg.From as the interest update target, which in repayment flows refers to the collateral token process—not the borrower. Consequently, the system updates the interest balance for an incorrect user and skips the actual borrower, allowing them to underpay or bypass interest accrual entirely. Additionally, there is no validation to ensure that msg.Tags.Sender or msg.Tags["X-On-Behalf"] is a properly formed address before updating interest. This opens the door to further inconsistencies or even execution errors if unexpected data is received in those fields.

## Recommendation
The logic in syncInterests should be corrected to check msg.Tags["X-Action"] == Repay, in combination with Action == Credit-Notice and msg.From == CollateralID before falling back to msg.Tags.Action, ensuring that repayment actions are properly routed. When X-Action is "Repay", the function should also validate that either msg.Tags["X-On-Behalf"] or msg.Tags.Sender is a valid address using the existing assertions.isAddress helper before proceeding with the interest update. This ensures the correct borrower’s interest is updated, prevents misuse via malformed tags, and aligns with the repayment flow conventions of the protocol.
