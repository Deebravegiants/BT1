# [M] Key transfer will destroy key if from==to

## Summary
Severity: Medium
Contest weight: 0.1739
Dataset id: 1201
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the `transferFrom` function of the Unlock protocol’s key management contract. When the caller attempts to transfer a key from an address to the same address (i.e., `_from == _recipient`), the function executes a series of state changes that unintentionally destroy the key. The root cause is the absence of a guard against self‑transfer; the logic proceeds to deduct a transfer fee, incorrectly adjusts the key’s expiration time, and finally marks the key as expired and resets the owner’s key identifier to zero. An attacker or a careless user can exploit this by invoking `transferFrom` with identical source and destination parameters, causing the key to vanish without any compensation. The impact is the loss of the user’s access rights associated with the key and the disappearance of any remaining value, as the protocol does not issue a refund for the destroyed key. This condition only manifests when a valid, non‑expired key exists and the function is called with matching `_from` and `_recipient` arguments. All key owners and any parties relying on the protocol’s subscription model are affected because their entitlement can be removed silently. The issue was uncovered during a manual audit by Code4rena, where the execution flow of `transferFrom` was traced line‑by‑line, revealing the unintended expiration step. The problem is subtle because a self‑transfer is rarely performed, so the bug does not surface in typical usage patterns and may be dismissed as a harmless no‑op. To remediate, the contract should explicitly reject self‑transfers by adding a `require(_from != _recipient, "TRANSFER_TO_SELF")` check at the start of the function, thereby preserving the key’s state and preventing accidental destruction. Conceptually, this bug belongs to the class of improper state transition vulnerabilities where edge‑case inputs lead to inconsistent or destructive state changes, violating the protocol’s accounting assumptions that keys remain valid unless explicitly revoked or expired by protocol logic.

## Proof of Concept
By following `transferFrom`’s execution: <https://github.com/code-423n4/2021-11-unlock/blob/main/smart-contracts/contracts/mixins/MixinTransfer.sol#L109:#L166> One can see that in the case where `_from == _recipient` with a valid key:
  * The function will deduct transfer fee from the key
  * The function will incorrectly add more time to the key’s expiration ([L151](https://github.com/code-423n4/2021-11-unlock/blob/main/smart-contracts/contracts/mixins/MixinTransfer.sol#L151))
  * The function will expire and reset the key ([L155](https://github.com/code-423n4/2021-11-unlock/blob/main/smart-contracts/contracts/mixins/MixinTransfer.sol#L155:#L158))

Therefore, the user will lose his key without getting a refund.

## Recommendation
Add a require statement in the beginning of `transferFrom`: `require(_from != _recipient, 'TRANSFER_TO_SELF');`

Fixed since then :)
