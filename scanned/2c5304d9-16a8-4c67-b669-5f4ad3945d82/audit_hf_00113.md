# [H] Wrong liquidation logic

## Summary
Severity: High
Contest weight: 0.2058
Dataset id: 232
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `belowMaintenanceThreshold` function decides if a trader can be liquidated:

    function belowMaintenanceThreshold(CrossMarginAccount storage account)
        internal
        returns (bool)
    {
        uint256 loan = loanInPeg(account, true);
        uint256 holdings = holdingsInPeg(account, true);
        // The following should hold:
        // holdings / loan >= 1.1
        // =>
        return 100 * holdings >= liquidationThresholdPercent * loan;
    }

The inequality in the last equation is wrong because it says the higher the holdings (margin + loan) compared to the loan, the higher the chance of being liquidated. The inverse equality was probably intended `return 100 * holdings <= liquidationThresholdPercent * loan;`. Users that shouldn’t be liquidated can be liquidated, and users that should be liquidated cannot get liquidated.

## Recommendation
No recommendation
