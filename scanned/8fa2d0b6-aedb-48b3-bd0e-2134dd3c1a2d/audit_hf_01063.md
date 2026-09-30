# [H] GG-2 | Reenter Dividends

## Summary
Severity: High
Contest weight: 0.0719
Dataset id: 4050
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a classic reentrancy flaw that appears in the dividend distribution routine of the contract. When a user requests a dividend payout, the contract first performs an external call that transfers BNB to the caller and only afterwards updates the internal recordthat tracks how much dividend the caller has already received. Because the state change occurs after the external call, a malicious contract can implement a fallback function that re‑enters the dividend function before the record is updated. Each re‑entry triggers another transfer of the same dividend amount, allowing the attacker to repeatedly drain BNB from the contract. This exploit can be carried out whenever a dividend claim is made, so any legitimate user who initiates a claim may unintentionally trigger the re‑entrancy if the caller is a contract under attacker control. The impact is a loss of funds from the dividend pool, resulting in reduced or missing payouts for honest participants and a breach of the protocol’s accounting guarantees that dividends should be distributed exactly once per entitlement period. The issue was discovered during a manual security audit that examined the order of operations in the payout function and noticed that the balance update was placed after the external call, a pattern known to be vulnerable to re‑entrancy. The bug can be hard to notice because the function appears to send the correct amount and may work correctly for externally owned accounts, masking the problem until a contract with a malicious fallback is used. To remediate the flaw, the contract should follow the check‑effects‑interactions pattern by updating the dividend ledger before any external call, or it should protect the function with a nonReentrant modifier from OpenZeppelin’s ReentrancyGuard, ensuring that a second entry cannot occur until the first execution finishes. Fixing the issue restores the intended business logic that each user receives exactly their entitled dividend and prevents the contract’s funds from being siphoned away through repeated re‑entries.

## Recommendation
Add a nonReentrant modiﬁer from OpenZeppelin’s ReentrancyGuard or utilize the check-effects-interactions pattern.
