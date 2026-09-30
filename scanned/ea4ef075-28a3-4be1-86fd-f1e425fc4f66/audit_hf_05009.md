# [M] Team Address Update Fails to Transfer Accrued Tokens

## Summary
Severity: Medium
Contest weight: 0.3485
Dataset id: 22998
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a function that allows the contract owner to update the stored team address, but the implementation does not include any logic to transfer the tokens that have accrued to the previous address. Consequently, when the team address is changed, the token balance that belongs to the team remains locked under the old address and the new address receives no tokens. The root cause is an incomplete state migration: the address variable is overwritten without invoking the token contract's transfer or balance‑migration routine, so the accounting entry for accrued rewards is left behind. An attacker or even the legitimate team can trigger the address change, causing the accrued tokens to become inaccessible and effectively disappear from the protocol’s accounting. From a user perspective, the UI may show that the team address update succeeded, yet the expected token payout is zero, leading to missing balances, empty refunds, or rewards that never arrive. This issue was discovered during a manual audit of the contract’s state‑changing functions, where the auditor noticed that the address update did not interact with the token balance. The bug is hard to notice because no transaction reverts and no explicit error is emitted; the contract simply records the new address while silently leaving the tokens stranded. The impact is a loss of funds for the team and potentially for users who rely on the team’s share of fees, breaking the business logic that accrued rewards must follow the designated beneficiary. To remediate, the update function should explicitly transfer the accrued token balance from the old address to the new address, or the contract should be refactored to tie token ownership to a role rather than a mutable address, ensuring that any change of beneficiary also migrates the associated assets. This class of flaw is commonly referred to as an “incomplete asset migration on address change” or “missing transfer on state update”, which violates accounting assumptions and can lead to funds disappearing after administrative actions.

## Recommendation
}
