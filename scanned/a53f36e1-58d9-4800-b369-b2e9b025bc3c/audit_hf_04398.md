# [M] In `CDPVault::liquidatePositionBadDebt`

## Summary
Severity: Medium
Contest weight: 0.6290
Dataset id: 21726
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the liquidation routine that handles bad‑debt positions. The function calculates the loss by taking the total debt, which is defined as principal plus accrued interest, and subtracting the amount that the liquidator repays. Because accrued interest is intended to be treated as profit for the protocol, including it in the loss computation reverses the accounting logic: when the repayment amount exceeds the principal, the contract records a loss instead of a profit. This mis‑calculation can be triggered whenever an unsafe position is liquidated through the `liquidatePositionBadDebt` entry point and the caller supplies a `repayAmount` larger than the outstanding principal debt. An attacker can deliberately choose such a repayment amount to cause the protocol’s profit accounting to show a deficit, effectively eroding the interest revenue that should belong to lenders or token holders. From a user perspective the symptoms are that after a liquidation the expected interest earnings disappear, the protocol may display a negative profit figure, or the liquidator receives less collateral than anticipated. The issue was uncovered during a Code4rena audit by reviewing the loss computation logic and comparing it with the profit calculation used in the regular `liquidatePosition` function. The bug is subtle because the same `calcTotalDebt` helper is used throughout the contract, making the sign error easy to overlook, and the loss variable is only used for internal accounting, not directly exposed to external callers. To remediate the problem the loss should be calculated using only the principal component, i.e., `debtData.debt - repayAmount`, while the accrued interest should be recorded as profit. Adjusting the formula restores the intended accounting invariant that interest accrues as revenue and only the principal can be lost during a bad‑debt liquidation.

## Proof of Concept
```solidity
function liquidatePositionBadDebt(address owner, uint256 repayAmount) external whenNotPaused {
        // validate params
        if (owner == address(0) || repayAmount == 0) revert CDPVault__liquidatePosition_invalidParameters();

        // load configs
        VaultConfig memory config = vaultConfig;
        LiquidationConfig memory liqConfig_ = liquidationConfig;

        // load liquidated position
        Position memory position = positions[owner];
        DebtData memory debtData = _calcDebt(position);
        uint256 spotPrice_ = spotPrice();
        if (spotPrice_ == 0) revert CDPVault__liquidatePosition_invalidSpotPrice();
        // verify that the position is indeed unsafe
        if (_isCollateralized(calcTotalDebt(debtData), wmul(position.collateral, spotPrice_), config.liquidationRatio))
            revert CDPVault__liquidatePosition_notUnsafe();

        // load price and calculate discounted price
        uint256 discountedPrice = wmul(spotPrice_, liqConfig_.liquidationDiscount);
        // Ensure that the debt is greater than the collateral at discounted price
        if (calcTotalDebt(debtData) <= wmul(position.collateral, discountedPrice)) revert CDPVault__noBadDebt();
        // compute collateral to take, debt to repay
        uint256 takeCollateral = wdiv(repayAmount, discountedPrice);
        if (takeCollateral < position.collateral) revert CDPVault__repayAmountNotEnough();

        // account for bad debt
        takeCollateral = position.collateral;
        repayAmount = wmul(takeCollateral, discountedPrice);
        uint256 loss = calcTotalDebt(debtData) - repayAmount;

        // transfer the repay amount from the liquidator to the vault
        poolUnderlying.safeTransferFrom(msg.sender, address(pool), repayAmount);

        position.cumulativeQuotaInterest = 0;
        position.cumulativeQuotaIndexLU = debtData.cumulativeQuotaIndexNow;
        // update liquidated position
        position = _modifyPosition(
            owner,
            position,
            0,
            debtData.cumulativeIndexNow,
            -toInt256(takeCollateral),
            totalDebt
        );

        pool.repayCreditAccount(debtData.debt, 0, loss); // U:[CM-11]
        // transfer the collateral amount from the vault to the liquidator
        token.safeTransfer(msg.sender, takeCollateral);

        int256 quotaRevenueChange = _calcQuotaRevenueChange(-int(debtData.debt));
        if (quotaRevenueChange != 0) {
            IPoolV3(pool).updateQuotaRevenue(quotaRevenueChange); // U:[PQK-15]
        }
}
```

In the `liquidatePositionBadDebt` function, the calculation of the loss is done by subtracting the repaid portion of the debt from the total debt.

```solidity
function calcTotalDebt(DebtData memory debtData) internal pure returns (uint256) {
        return debtData.debt + debtData.accruedInterest; //+ debtData.accruedFees;
}
```

Through the `calcTotalDebt()` function, we know that the total debt includes both the principal debt and the interest accrued on the debt. In this CDPVault, the interest accrued on the debt is treated as profit. For example, in the `liquidatePosition` function, profit is calculated as `debtData.accruedInterest`, and this profit is treated as interest revenue in other functions as well.

```solidity
function liquidatePosition(address owner, uint256 repayAmount) external whenNotPaused {
        //skip ........
        uint256 newDebt;
        uint256 profit;
        uint256 maxRepayment = calcTotalDebt(debtData);
        uint256 newCumulativeIndex;
        if (deltaDebt == maxRepayment) {
            newDebt = 0;
            newCumulativeIndex = debtData.cumulativeIndexNow;
            profit = debtData.accruedInterest;
            position.cumulativeQuotaInterest = 0;
        } 

        //skip ........
}
```

Therefore, the loss should only account for the loss of the principal amount. In the `liquidatePositionBadDebt` function, if `repayAmount > debtData.debt`, there would actually be a small profit (`repayAmount - debtData.debt`) instead of a loss. The calculation for the loss should be `debtData.debt - repayAmount` to correctly reflect the loss of the principal portion.

## Recommendation
Modify the relevant formula for calculating the loss.
