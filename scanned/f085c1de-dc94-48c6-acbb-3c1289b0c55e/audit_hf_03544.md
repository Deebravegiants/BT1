# [M] GLPM-3 | Additional Ether Lost

## Summary
Severity: Medium
Contest weight: 0.0410
Dataset id: 19346
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an over‑payment and missing‑refund bug in the migration function of the contract. When a caller invokes migrate and supplies a msg.value that exceeds the required execution fee multiplied by the number of migration items, the contract does not return the surplus Ether to the caller. The root cause is the absence of a validation check that enforces msg.value to equal executionFee * migrationItems.length and the lack of a refund mechanism for any excess amount. An attacker can exploit this by deliberately sending more Ether than required; the contract will retain the extra funds, which become available to the next address that calls migrate, effectively allowing the attacker to capture Ether that should have been refunded. The impact is a loss of user funds: a user who overpays sees a reduced balance after the transaction, and the subsequent caller can withdraw the unrefunded Ether, leading to unintended transfer of value. This condition occurs only when the supplied Ether is greater than the exact fee needed for the migration batch; normal calls with exact payment are unaffected. All participants who can call migrate – typically any external account – are potentially affected, especially those who unintentionally overpay. The issue was discovered during a manual audit that examined the fee calculation logic and noticed the missing equality check and refund path. It can be hard to notice because the transaction does not revert and appears successful, while the excess Ether silently disappears from the sender’s balance, producing a subtle discrepancy that may only be observed when comparing expected versus actual post‑transaction balances. To remediate, the contract should enforce that msg.value matches the exact required fee and, if any surplus is detected, automatically refund the difference to the caller before proceeding with the migration logic. This aligns the implementation with standard accounting principles that require precise payment handling and prevents unintended fund loss, restoring trust that users receive exactly the amount they expect to pay and no more.

## Recommendation
Add validation to ensure that msg.value == executionFee * migrationItems.length, otherwise refund any excess Ether to the caller.
