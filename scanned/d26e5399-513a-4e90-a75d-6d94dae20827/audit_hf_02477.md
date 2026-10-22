# [M] Improper Logic Of settlementBorrow()

## Summary
Severity: Medium
Contest weight: 0.3569
Dataset id: 13247
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the settlementBorrow function, which is intended to finalize a borrowing operation only when the loan is in a specific terminal state. The implementation performs a require check that the stored borrowInfo.state equals the numeric constant 9, but the surrounding logic contains redundant or misplaced code that can bypass or invalidate this check under certain execution paths. As a result, the function may be invoked when the loan is not actually settled, allowing the contract to execute settlement steps such as transferring collateral or updating balances in an inappropriate context. This improper logic stems from an inaccurate state validation and the presence of dead code that does not contribute to the intended safety guarantees. An attacker or a careless user could trigger settlementBorrow with a bid that is still active, causing the contract to move funds according to the settlement routine even though the loan has not reached the required state. The impact includes potential loss of collateral, funds becoming inaccessible, or the accounting of the protocol becoming inconsistent – for example, a user may see their balance drop to zero after calling settlementBorrow, or a loan may appear settled while it is still outstanding. The issue manifests when the function is called with a bid identifier whose associated borrowInfo.state is not 9, yet the redundant logic allows the function to proceed without reverting. All participants that rely on the borrowing module – borrowers, lenders, and the protocol itself – are affected because the core financial invariant that a loan can only be settled after full repayment is broken. The flaw was discovered during a manual audit of the contract source, where the auditor noticed that the require statement was followed by code that never altered the state condition, indicating a logical inconsistency. Because the function does not emit clear error messages or revert in all invalid cases, the problem can be subtle and may only surface when users experience unexpected zero balances or missing refunds. To remediate the issue, the redundant code should be removed and the state validation tightened so that settlementBorrow can only execute when the borrowInfo.state is definitively the terminal settled state, with proper checks and events to guarantee that no funds are moved unless the loan is truly closed.

## Recommendation
Remove the redundant code from the settlementBorrow() routine safely.
