# [M] M-03 | Paused State Leads To Forced Defaults

## Summary
Severity: Medium
Contest weight: 0.0316
Dataset id: 20864
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a pause‑related access control flaw in the NFTYFinanceV1 contract that prevents borrowers from executing the loan repayment function when the contract owner activates the paused state. The root cause is that the makeLoanPayment function is guarded by the same pause modifier that is intended to halt only non‑essential operations, so when the contract is paused the repayment path is unintentionally blocked. An attacker or even a well‑meaning owner can trigger the pause, after which any borrower with an outstanding loan is unable to submit a payment transaction; the transaction reverts and the loan remains outstanding. Because the protocol’s accounting assumes that borrowers can always repay before the loan term expires, the inability to pay forces the loan into default according to the contract’s logic, which then automatically seizes the NFT collateral that backs the loan. From the user’s perspective the expected outcome – a successful repayment and retention of the NFT – is replaced by a situation where the UI shows the loan balance unchanged, the repayment button is disabled, and eventually the collateral disappears from the user’s wallet. This issue is discovered during a manual audit that examined the interaction between the pause mechanism and core financial functions. It can be hard to notice because pausing is generally regarded as a safety feature, and the contract’s documentation may not highlight that repayment is also paused, leading developers and auditors to assume that only administrative functions are affected. The impact is financial loss for borrowers, erosion of trust in the protocol, and potential liability for the protocol operators, as users may be forced to lose valuable NFTs without any chance to settle their debt. The bug belongs to the class of “paused‑state forced default” or “emergency‑stop misuse” vulnerabilities, where an emergency control unintentionally disables critical user‑initiated actions, breaking business logic that relies on continuous availability of payment pathways. To remediate the issue the contract should decouple the pause protection from the repayment function, either by exempting makeLoanPayment from the pause modifier or by introducing a separate pause flag that only affects non‑critical operations, ensuring that borrowers retain the ability to settle their loans even when the protocol is in an emergency state.

## Recommendation
Consider allowing the makeLoanPayment function to be called when the protocol is paused.
