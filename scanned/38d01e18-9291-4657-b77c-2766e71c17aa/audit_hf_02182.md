# [H] Improved Logic in PCT::ensureUpperBoundLimit()

## Summary
Severity: High
Contest weight: 0.6184
Dataset id: 12174
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To improve the capital efficiency, the handle.fi protocol further supports the integration of external protocols for increased return. Accordingly, it maintains necessary accounting to keep track of the investment and gains about each external investment protocol. While examining the current accounting logic, we notice a specific function fails to properly maintain the accounting. To elaborate, we show below the full implementation of the ensureUpperBoundLimit() function, which checks the Treasury's collateral balance and total invested funds against maximum upper bound and withdraws from external protocol into Treasury if needed. Our analysis shows that it properly withdraws the funds from the external investment protocol and reduce the totalInvestments state. However, it fails to update the protocolInvestments state and it may corrupt the execution of a number of related functions, e.g., withdrawProtocolFunds().
```solidity
function ensureUpperBoundLimit(
    IPCTProtocolInterface pi,
    address collateralToken
) private {
    Pool storage pool = pools[collateralToken];
    uint256 totalInvested = pool.protocolInvestments[address(pi)];
    uint256 totalFunds = IERC20(collateralToken).balanceOf(address(treasury)).add(
        totalInvested
    );
    uint256 upperBound = handle.pctCollateralUpperBound();
    uint256 maxInvestmentAmount = totalFunds.mul(upperBound).div(1 ether);
    if (totalInvested <= maxInvestmentAmount) return;
    // Upper bound limit has been exceeded; withdraw from external protocol.
    uint256 diff = totalInvested.sub(maxInvestmentAmount);
    pi.withdraw(diff);
    pool.totalInvestments = pool.totalInvestments.sub(diff);
}
```

## Recommendation
Revise the ensureUpperBoundLimit() implementation to properly keep track of the investment-related accounting.
