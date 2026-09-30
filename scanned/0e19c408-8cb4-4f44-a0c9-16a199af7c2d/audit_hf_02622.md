# [H] Two nonReentrancy Modifiers Prevent liquidate() Execution

## Summary
Severity: High
Contest weight: 0.2507
Dataset id: 14158
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Two nonReentrant modifiers are executed in a single call, causing ReentrancyGuard to revert during liquidate().  
When the function AbstractLender.liquidate() is called, the following call sequence occurs.  
1. AbstractLender.liquidate() is called on the lender contract. The function has a nonReentrant modifier. At this point, _reentrancyStatus is set to _REENTRANCY_ENTERED.  
2. IPeerToPeerOpenTermLoan(loanAddr).liquidate() is called on the respective loan contract. This code may execute InitializableOpenTermLoan.liquidate().  
3. IHookableLender(lender).notifyLoanMatured() is called on the lender contract. The function has a nonReentrant modifier as described in HookableLender.sol.  
Since the _reentrancyStatus of the lender contract was already set to _REENTRANCY_ENTERED in step (1), the call in step (3) would cause a revert on BaseReentrancyGuard._nonReentrantBefore(). The result is, AbstractLender.liquidate() will revert.  
The impact is rated as medium severity as being unable to call liquidate() prevents losses being accounted for at the pool level.

## Recommendation
Consider removing one of the nonReentrant modifiers either on AbstractLender or HookableLender contract.
