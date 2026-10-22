# [M] Proper Debt Absorb in absorbDebt()

## Summary
Severity: Medium
Contest weight: 0.4409
Dataset id: 12172
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Within the handle.fi protocol, there is a scalable pool that is designed to collectively fund liquidations. The pool holders share potential loss from the liquidation and are also potentially rewarded with liquidated collaterals. While examining the current debt-socializing logic, we notice the current implementation can be improved. To elaborate, we show below the full implementation of the absorbDebt() function. It is designed to update various pool parameters after performing a liquidation. It comes to our attention that the totalDeposits is not updated until the debt loss has been socialized to all share holders. For better accuracy, it is suggested to reduce the totalDeposits before socializing the debt.
```solidity
function absorbDebt(
    uint256 debt,
    address[] memory collateralTypes,
    uint256[] memory collateralAmounts,
    address fxToken
) private {
    if (pools[fxToken].totalDeposits == 0 || debt == 0) return;
    // Increase pool collateral balances.
    uint256 l = collateralTypes.length;
    for (uint256 i = 0; i < l; i++) {
        if (collateralAmounts[i] == 0)
            continue;
        pools[fxToken].collateralBalances[collateralTypes[i]] = pools[
            fxToken
        ].collateralBalances[collateralTypes[i]].add(collateralAmounts[i]);
    }
    _updateFxLossPerUnitStaked(
        debt,
        collateralTypes,
        collateralAmounts,
        fxToken
    );
    _updateCollateralGainSums(collateralTypes, collateralAmounts, fxToken);
    _updateSnapshotValues(debt, fxToken);
    pools[fxToken].totalDeposits = pools[fxToken].totalDeposits.sub(debt);
}
```

## Recommendation
Revise the absorbDebt() implementation to properly socialize the debt loss to all share holders.
