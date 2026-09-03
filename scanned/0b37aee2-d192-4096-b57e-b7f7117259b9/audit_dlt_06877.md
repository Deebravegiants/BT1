# [H] Wrong liquidation logic

## Summary
Severity: High
Chain: Smart contract
Component: 2021-04-marginswap
Published: 2021-04-07
Source: https://github.com/code-423n4/2021-04-marginswap-findings/issues/23
Type: code-finding

## Details
# Eth address

0x6823636c2462cfdcD8d33fE53fBCD0EdbE2752ad


# Vulnerability details

The `belowMaintenanceThreshold` function decides if a trader can be liquidated:

```solidity
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
```

The inequality in the last equation is wrong because it says the higher the holdings (margin + loan) compared to the loan, the higher the chance of being liquidated.
The inverse equality was probably intended `return 100 * holdings <= liquidationThresholdPercent * loan;`.



# Impact

Users that shouldn't be liquidated can be liquidated, and users that should be liquidated cannot get liquidated.


# Recommended mitigation steps

Fix the equation.



_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-04-marginswap-findings/issues/23_
