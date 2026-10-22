# [M] M-09 | User GLV Deposits Errantly Maximized

## Summary
Severity: Medium
Contest weight: 0.2115
Dataset id: 21890
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _getMintAmount function the poolValue used to compute the value of the depositor’s GM tokens is maximized to avoid applying a double spread from the GLV value computation. However the computation of the GLV value is not guaranteed to have a maximizing effect in excess of the maximizing effect experienced by the depositor. For example: • GLV is supports Markets A, B, and C • GLV totalSupply is 100 • GLV holds 10 GM A, 10 GM B, and 0 GM C • The minimum price of GM A is $1 and the maximum is $1.01 • The minimum price of GM B is $1 and the maximum is $1.01 • The minimum price of GM C is $1 and the maximum is $1.05 due to indexToken spread, trader pnl, impact pool amount, etc… • User A deposits 10 GM C tokens • The GLV value if minimized is $20, User A’s deposits is $10 if minimized, User A would receive 50 GLV tokens if both were minimized • The GLV value since it is maximized is $20.20, User A’s deposit is valued at $10.50 since it is maximized • As a result the maximization of both of these values positively affects User A such that they now receive $10.50/$20.20 * 100 ~= 51.98 GLV Due to the maximization of both values in this example, User A receives roughly 2 more GLV tokens than if the values were to not be maximized. Additionally, the same effect would apply if a user is simply depositing more $ value than the GLV currently holds, since the maximization would have a greater absolute value impact on the numerator than the denominator due to being applied for a larger size.

## Recommendation
Consider valuing the GLV value at the maximum, while valuing the user’s deposits at the minimum to ensure that under no circumstances the protocol is rounding in the user’s favor. Additionally, consider applying the same spread to withdrawals to protect the protocols from these cases. This behavior will negatively impact users, but protect against profitable arbitrages.
