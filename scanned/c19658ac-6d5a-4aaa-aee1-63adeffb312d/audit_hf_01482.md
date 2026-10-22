# [M] M-6 Unexpected PERMIT_CODE in RouterV2

## Summary
Severity: Medium
Contest weight: 0.0399
Dataset id: 7862
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from an implicit assumption in the RouterV2 contract that a PERMIT operation (identified by PERMIT_CODE) will always appear as the first element in a list of batched actions. The checkTo() function, which determines the target address for subsequent operations, is written to treat the first element specially and does not contain logic to handle a PERMIT_CODE that appears later in the sequence. When a caller includes a PERMIT operation after other actions, checkTo() fails to recognise the correct destination and returns the zero address. This mis‑routing can cause the router to attempt to forward funds or execute calls to address(0), effectively burning tokens or causing the intended recipient to receive nothing. The issue is triggered only when the ordering constraint is violated, which may not be obvious during normal usage because most callers place PERMIT first, making the bug hard to detect without targeted testing. It was discovered during a systematic audit by MixBytes, which examined the control‑flow of the router and identified the unchecked assumption. Exploitation does not require privileged access; an attacker can simply craft a transaction that places PERMIT_CODE later in the operation array, causing the router to return zero from checkTo() and leading to loss of funds or failed operations. Affected parties include any user or protocol that relies on RouterV2 for token swaps, cross‑chain transfers, or permissioned actions, as their balances may appear unchanged or tokens may be unintentionally burned. From a user perspective the symptom is that a transaction that should result in a token transfer completes without error but the user’s balance remains unchanged, or the transaction reverts because the contract attempted to interact with the zero address. The bug violates the business logic that assumes a valid destination address for every operation, breaking accounting guarantees. The recommended remediation is to enforce the ordering rule explicitly—reject any batch where PERMIT_CODE is not the first element—or to modify checkTo() so that it correctly resolves the target address regardless of where PERMIT appears, thereby restoring the intended routing semantics.

## Recommendation
We recommend ensuring that the PERMIT operation is either the first in the sequence or not included at all.
