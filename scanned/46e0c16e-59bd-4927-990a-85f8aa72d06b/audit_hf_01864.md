# [M] M-9 The owner can remove themselves

## Summary
Severity: Medium
Contest weight: 0.0323
Dataset id: 10373
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an owner self‑removal flaw in the contract's role‑management logic. The update‑role function does not prevent the current owner from calling the removal routine on their own address, which means the owner can unintentionally or maliciously renounce their privileged role without any fallback administrator being left in place. This occurs because the access‑control check only verifies that the caller is an authorized role, but it does not enforce a rule that at least one owner must remain after the operation. When the owner removes themselves, any function that requires the owner role reverts or becomes a no‑op, effectively halting the protocol's administrative capabilities. From a user's perspective the UI may suddenly stop showing admin buttons, transactions that previously required owner approval start failing, and deposits or withdrawals may be blocked because the contract can no longer execute privileged logic. The impact is a denial‑of‑service condition: the system is blocked, funds may become inaccessible, and the protocol cannot be upgraded or maintained. The issue is discovered during a manual audit of the role‑update code where the author noticed that the removal path does not contain a safeguard against zero owners. It can be hard to notice because self‑renunciation is a common pattern in many contracts, yet in this design there is no alternative owner to take over, so the problem only surfaces after the owner actually executes the removal. To remediate, the contract should either forbid the owner from removing themselves, require a multi‑step handover to a new owner, or enforce that at least one owner address remains after any removal operation. This class of bug belongs to privilege‑loss or access‑control misconfiguration where a critical role can be eliminated without a replacement, breaking business logic that assumes an always‑present administrator.

## Recommendation
We recommend restricting the owner's ability to remove themselves and creating a separate function for such actions.
