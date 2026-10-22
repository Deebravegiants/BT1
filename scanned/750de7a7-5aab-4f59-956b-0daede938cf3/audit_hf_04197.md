# [H] Signatures can be replayed in `withdraw`

## Summary
Severity: High
Contest weight: 0.0554
Dataset id: 21001
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a signature replay flaw in the withdraw function of the TimelockTokenPool contract. The function accepts an off‑chain signed message that authorises a token transfer, but it does not keep any state that prevents the same signed message from being processed more than once. Because there is no nonce, timestamp, or other replay‑prevention mechanism, an attacker who obtains a legitimate withdrawal signature from a user can submit that signature repeatedly and cause the contract to transfer the authorized amount each time. This can be exploited by simply calling withdraw with the same parameters and signature in a loop, or by forwarding the signature to other accounts. The impact is that the pool can lose more tokens than the user intended, effectively allowing funds to disappear from the contract and leaving users with reduced balances or zero refunds. The issue manifests whenever a user signs a withdrawal request and the contract processes it without checking whether the signature has already been used. All users who rely on signed withdrawal messages are affected, as are the protocol’s overall token accounting and any parties that trust the pool’s integrity. The flaw was discovered during a formal security audit that examined the signature verification logic and noticed the absence of a replay‑prevention field. It can be hard to notice because the transaction succeeds, the UI may show the correct amount withdrawn, yet the pool’s total balance shrinks unexpectedly. The bug belongs to the class of replay attacks on signed messages, similar to missing nonce bugs in off‑chain authorization schemes. To remediate, the contract should incorporate a unique identifier such as a per‑user nonce, a global counter, or a timestamp that is included in the signed payload and checked before processing. Once a signature is used, the corresponding nonce should be incremented or the signature marked as spent, preventing any further execution with the same data. This change restores the intended accounting guarantees and ensures that a user’s signed withdrawal can only be executed once.

## Recommendation
Consider using a nonce or other signature replay protection in the TimelockTokenPool contract.

Valid bug report, trying to fix it in this PR: <https://github.com/taikoxyz/taiko-mono/pull/16611/files>
