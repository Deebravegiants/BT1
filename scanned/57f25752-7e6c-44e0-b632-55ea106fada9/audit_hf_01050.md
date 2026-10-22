# [H] H-01 | Incorrect Calculation Of totalFees In updateNav

## Summary
Severity: High
Contest weight: 0.3168
Dataset id: 4024
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The totalFees variable is intended to represent the total fees affecting the asset flow between the vault and the manager during an NAV update. However, the calculation is inconsistent:
• accruedManagerPerformanceFees and accruedManagerTvlFees are cumulative (including fees from all previous epochs plus the current epoch's managerPerformanceFee and managerTvlFee).
• brktTvlFee is the new fee for the current epoch only, not the cumulative accruedBrktTvlFees.
This inconsistency leads to an incorrect totalFees value. Since totalFees is used in totalDebit = withdrawalAssets + totalFees within _processDepositsWithdrawals, it determines how much the manager must transfer to the vault (or receive from it). Using cumulative fees for manager fees is incorrect.
Expected Behavior: As the fees are now "locked on the vault's balance" the vault should retain all accrued fees and the manager should only need to cover the net asset flow (withdrawalAssets - depositAssets) plus the new fees for the current epoch. The previously accrued fees are already in the vault and can be used to pay withdrawals or claimed fees.
Example:
• Epoch 1: brktTvlFee = 5, so accruedBrktTvlFees = 5.
• Epoch 2: brktTvlFee = 3, so accruedBrktTvlFees = 8. Current code computes totalFees = accruedManagerFees + accruedManagerTvlFees + 3, ignoring the prior 5 in accruedBrktTvlFees. It should use only new fees (managerPerformanceFee + managerTvlFee + brktTvlFee).

## Recommendation
Use only the new fees for consistency and logical correctness:
uint256 totalFees = managerPerformanceFee + managerTvlFee + brktTvlFee;
This ensures the manager transfers funds to cover withdrawals and new fees, while the vault retains previously accrued fees, aligning with the locking mechanism.
