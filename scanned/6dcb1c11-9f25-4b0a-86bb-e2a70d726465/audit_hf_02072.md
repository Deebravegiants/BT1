# [M] Improved Logic of Calculation For principalLost Amount

## Summary
Severity: Medium
Contest weight: 0.4513
Dataset id: 11743
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BNPL Pay protocol allows the user to create, and operate a pool of liquidity that is delegated to them from lenders. When the capital loss is incurred from loan defaults, the slashing occurs. The percentage slashing penalty will be equivalent to the size of the default as a percentage of the total pool capital. While examining this part of logic, we notice an issue in current implementation. To elaborate, we show below the related routines.

```solidity
function slashLoan(uint256 loanId, uint256 minOut)
external
ensurePrincipalRemaining(loanId)
{
    // Step 1. load loan as local variable
    Loan storage loan = idToLoan[loanId];
    // Step 4. calculate the amount to be slashed
    uint256 principalLost = loan.principalRemaining;
    // Check if there was a full recovery for the loan, if so
    if (baseTokenOut >= principalLost) {
        // slash loan only if losses are greater than recovered
    } else {
        // safe div: principal > 0 => totalAssetValue > 0
        uint256 slashPercent = (1e12 * principalLost) /
            getTotalAssetValue();
        uint256 unbondingSlash = (unbondingAmount * slashPercent) / 1e12;
        uint256 stakingSlash = (getStakedBNPL() * slashPercent) / 1e12;
        // Step 5. deduct slashed from respective balances
        accountsReceiveable -= principalLost;
        slashingBalance += unbondingSlash + stakingSlash;
        unbondingAmount -= unbondingSlash;
    }
}
```

The slashLoan() routine implements a rather straightforward logic in allowing the users to declare a loan defaulted and slash the loan. It comes to our attention that the calculation of principalLost is using (1e12 * principalLost)/ getTotalAssetValue(). This logic makes an implicit assumption of principalLost is the total loss while this value should equal to principalLost - baseTokenOut.

## Recommendation
Revise the above slashLoan routine to properly compute the value of principalLost.
