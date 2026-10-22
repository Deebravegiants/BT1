# [M] EXTH-2 | Lack Of safeTransfer For Arbitrary Token

## Summary
Severity: Medium
Contest weight: 0.0389
Dataset id: 19335
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from the use of the standard ERC20 transfer function when the contract attempts to send an arbitrary refund token in the makeExternalCalls routine. Transfer simply forwards the call to the token contract and assumes success, but many ERC20 implementations deviate from the specification by returning a boolean value instead of reverting on failure. Because the code does not check the returned boolean, a token that returns false will cause the contract to believe the transfer succeeded while no tokens are actually moved. This can be exploited by an attacker who supplies a malicious or non‑standard token as the refundToken; the token’s transfer function can silently fail, allowing the contract to retain the funds that should have been refunded. The impact is that users requesting a refund may receive nothing, see their balances unchanged, or observe a successful transaction in the UI while the funds remain locked in the contract. The issue manifests only when the refundToken does not follow the expected revert‑on‑failure behavior, which is common for older or custom tokens. All participants who rely on the refund mechanism – typically end‑users and any downstream protocol that assumes refunds are honoured – are affected. The flaw was identified during a manual audit that highlighted the lack of a safety wrapper around external token transfers. Because the failure is silent, it can be difficult to notice without explicit return‑value checks or extensive testing with a variety of token contracts. The proper remediation is to replace direct calls to transfer with a safeTransfer pattern (for example, OpenZeppelin’s SafeERC20.safeTransfer) that validates the boolean result and reverts on failure, thereby guaranteeing that either the tokens are transferred or the transaction aborts. Conceptually, this belongs to the class of “unchecked external call” or “ERC20 transfer return‑value” bugs, where the contract assumes success without verification, breaking accounting assumptions and leading to potential loss of funds.

## Recommendation
Prefer safeTransfer to transfer.
