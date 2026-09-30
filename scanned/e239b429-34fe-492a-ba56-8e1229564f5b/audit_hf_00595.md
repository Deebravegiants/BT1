# [H] H-03 | Liquidity Providers Can Withdraw Right Away

## Summary
Severity: High
Contest weight: 0.1736
Dataset id: 2093
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current protocol design allows LPs to withdraw their liquidity at any time without any enforced
delay. The removeLiquidity function only checks that the total reserved USD is less than or equal to
the computed AUM.
As a result, LPs can instantly remove substantial amounts of collateral from a pool, increasing its
utilization and causing borrowing rates to spike dramatically.
Traders relying on a stable borrowing environment are suddenly forced to pay higher borrowing fees
or simply to close their positions as soon as possible.

## Recommendation
Implement a withdrawal delay mechanism that prevents LPs from instantly removing large amounts
of liquidity. By requiring a grace period before withdrawals are ﬁnalized, traders gain time to
anticipate these changes by adding collateral or closing their positions.
MCO_LIQUIDITY_LOCK_PERIOD should be way higher than the 2 minutes set in the different test
ﬁles.
