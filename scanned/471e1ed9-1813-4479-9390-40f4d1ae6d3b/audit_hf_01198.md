# [M] Net repayments can be counted across multiple solverOps

## Summary
Severity: Medium
Contest weight: 0.4264
Dataset id: 5203
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A solverOp's balance is considered reconciled if all current repayments are at least equal to all current borrows, and the solver has also prepaid their maximum gas liability, either through approving their bonded atlETH or with an excess repayment. This is implemented in the following code:
```solidity
function _isBalanceReconciled() internal view returns (bool) {
    // ...
    return (bL.repays >= bL.borrows) && (_maxApprovedGasValue + _netRepayments >= gL.solverGasLiability());
}
```
However, this logic does not function correctly when multipleSuccessfulSolvers == true, because the same net repayment can be counted toward multiple solverOps.
For example, if one solverOp leaves behind a 1 ETH net repayment and there are 10 solverOps, each can independently apply the same 1 ETH toward their own gas liability check. There is no mechanism to track how much of the repayment each solverOp is relying on, which allows the same ETH to be reused across multiple solverOps. As a result, _isBalanceReconciled() may incorrectly return true for all solverOps, even if the excess is only sufficient to cover one.
This can lead to a shortfall in the gas reimbursement that only becomes apparent during the final _settle() call, at which point the bundler would implicitly cover the difference.

## Recommendation
Change the gas accounting logic so that after each solverOp, the portion of the net repayment used toward its gas liability is subtracted out, preventing other solverOps from reusing the same amount.
