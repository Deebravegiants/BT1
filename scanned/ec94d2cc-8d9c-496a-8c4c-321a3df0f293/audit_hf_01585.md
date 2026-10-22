# [H] MJR-7 Possible transfer of bad account

## Summary
Severity: High
Contest weight: 0.0138
Dataset id: 8503
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the ability to transfer a credit account that is already under‑collateralised, i.e., its health factor (Hf) is below the safety threshold of 1, without any prior liquidation or explicit consent from the receiving party. The root cause is the lack of a validation step in the transfer function that checks the health factor of the source account before allowing the ownership change. Because the protocol does not enforce an approval or consent mechanism, a user who holds a bad account can invoke the transfer routine and assign the same account to another address. An attacker can therefore off‑load a risky position to an unsuspecting participant, who will inherit the under‑collateralised state and may be forced into liquidation at the next block. The impact is that the recipient may lose collateral, see their balance drop to zero, or experience unexpected liquidation events, effectively causing funds to disappear from their perspective. This situation occurs whenever an account’s health factor falls below 1 but the liquidation bot has not yet acted, and the contract’s transfer logic is called. All users of the CreditManager who rely on the ability to transfer accounts are affected, especially those who assume that transferred accounts are healthy. The issue was discovered during a manual audit of the Gearbox Protocol codebase, where the auditor noticed that the transfer path does not include any health‑factor guard or receiver approval. The bug is subtle because the transfer succeeds syntactically and the protocol does not emit a warning, so users may not realise they have inherited a failing position until liquidation occurs. To remediate, the contract should introduce an explicit approval step (e.g., an `approveTransfer` call) that requires the destination address to accept the account, and the transfer function should reject any account with Hf < 1 unless a special emergency flag is set. This aligns the implementation with the business logic that an account transfer should only occur for healthy positions, preserving accounting integrity and preventing accidental loss of funds.

## Recommendation
We recommend adding approve mechanic, so that account receiver does not receive account that he doesn't want.
