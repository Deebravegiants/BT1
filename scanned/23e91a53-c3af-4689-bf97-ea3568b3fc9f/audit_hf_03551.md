# [M] LGR-6 | Insurance Account May Become Insolvent

## Summary
Severity: Medium
Contest weight: 0.1207
Dataset id: 19353
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When liquidatable accounts cannot cover the liquidatorFee with their remaining margin, all positions in the account and the remaining margin balance are transferred to the insurance fund. In times of volatility, several accounts may become insolvent and all have their positions transferred to the insurance account. The insurance account may then find itself to be insolvent, in which case ADL will not be sufficient to remedy the situation. The insurance account is also intended to cover insolvent accounts where the settled PnL is more negative than the account margin. This behavior can also be a pathway for the insurance account to become insolvent, especially when combined with receiving positions from insolvent accounts.

## Recommendation
Though this scenario may be rare, it is a distinct possibility. Have a contingency plan in the event that this scenario ever plays out, for example a deposit can automatically be made for the insurance fund when it nears insolvency.
