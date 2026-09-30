# [C] Funds may be stolen by calling onMoreFlashLoan() directly

## Summary
Severity: Critical
Contest weight: 0.5130
Dataset id: 10557
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An unauthorized external call vulnerability exists in the flash‑loan strategy contract. The function onMoreFlashLoan is intended to be invoked only by the market contract that coordinates flash‑loan cycles. However, the implementation does not contain any check of msg.sender, so any address can call the function directly. When called, the function releases the collateral that was previously locked for the flash‑loan operation to the caller without verifying that the caller is the legitimate market. An attacker can therefore trigger the function, receive the locked collateral, and the original borrower loses the assets. The bug manifests when a malicious actor sends a transaction that calls onMoreFlashLoan with arbitrary parameters; no prerequisite flash‑loan execution is required. The impact is a loss of user funds and a breach of the protocol’s accounting guarantees, because the protocol assumes that only the market can move collateral after a flash‑loan. The issue was discovered during a manual audit that examined the control flow of flash‑loan related functions and noticed the missing require statement. Because the function name suggests internal use, the lack of an explicit access‑control modifier can be easy to overlook, especially if the function does not emit distinctive events. The vulnerability belongs to the class of missing access‑control or unauthorized external call bugs, which break the trust model of the contract. From a user perspective the symptom is that collateral disappears from their balance, or a refund that should be returned after a flash‑loan is missing, leading to a zero or reduced balance. The fix is to add a validation that the caller equals the market address (for example, using a require statement) or to restrict the function with an onlyMarket modifier, thereby ensuring that only the designated market contract can trigger the collateral release logic.

## Recommendation
Revert if the caller is not markets.
