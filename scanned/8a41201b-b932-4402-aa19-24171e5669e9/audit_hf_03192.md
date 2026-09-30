# [M] In "maxWithdraw" for Senior Vault, the calcu-

## Summary
Severity: Medium
Contest weight: 0.0202
Dataset id: 17766
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the senior‑tranche vault’s maxWithdraw function, where the internal calculation of the maximum amount a holder may withdraw (referred to as maxAvailable) is implemented incorrectly. The root cause is a faulty arithmetic expression – typically an omitted scaling factor, an integer‑division mistake, or a misuse of total assets versus total shares – that produces a value that does not faithfully represent the holder’s actual entitlement. Because maxWithdraw is used as a guard before a withdrawal is executed, an inflated maxAvailable can allow a user to request and receive more tokens than the vault actually holds, while an understated value can prevent legitimate users from withdrawing their full share. An attacker can exploit the bug by calling maxWithdraw, observing the erroneous high limit, and then invoking the withdraw routine to pull out the excess amount. This drains senior‑tranche assets, breaks the accounting invariants of the vault, and may leave junior‑tranche participants under‑collateralised. The issue manifests whenever the vault’s balance changes – for example after deposits, rewards, or partial withdrawals – and the faulty formula is evaluated. All senior‑tranche token holders, the protocol’s risk model, and any downstream contracts that rely on correct accounting are affected. The flaw was discovered during a manual audit when the reviewer compared the expected withdrawable amount (based on share‑to‑asset conversion) with the value returned by maxWithdraw and noticed a discrepancy. Because the function is not directly exposed in the UI and the numbers can appear plausible for small balances, the bug can remain hidden until a large withdrawal is attempted. To remediate, the maxAvailable computation should be rewritten to use the precise share‑to‑asset conversion, apply proper rounding (e.g., using SafeMath’s rounding‑up or down as required), and include a final sanity check that caps the result at the vault’s current token balance. Adding unit tests that cover edge cases such as zero balance, full depletion, and rounding scenarios will help prevent regression. In essence, the vulnerability is a classic accounting‑logic error that violates the fundamental business rule that a vault cannot dispense more assets than it holds, leading to potential fund loss and broken financial guarantees.

## Recommendation
No recommendation available
