# [M] Changes to `creatorFeeDecimal` and `operatorFeeDecimals` will retroactively apply to older bets

## Summary
Severity: Medium
Contest weight: 0.5824
Dataset id: 2732
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function setFees(uint16 _creatorFeeDecimal, uint16 _operatorFeeDecimal) external onlyRole(DEFAULT_ADMIN_ROLE) {
    creatorFeeDecimal = _creatorFeeDecimal;
    operatorFeeDecimal = _operatorFeeDecimal;
    emit MarketsFeesChanged(_creatorFeeDecimal, _operatorFeeDecimal);
}
```

```solidity
if (losingPotAmount > 0) {
    uint256 currentlyAvailable = availableLosingPot[marketCommitment];
    require(currentlyAvailable >= losingPotAmount, MarketsInvalidResult(marketCommitment, resultCommitment));
    availableLosingPot[marketCommitment] = currentlyAvailable - losingPotAmount;

    // only charge fees on the losing pot, to discourage markets that
    // are heavily imbalanced. If the losing pot is small (because it's
    // a very unlikely result), then creator fees are also small
    uint256 creatorFee = (creatorFeeDecimal * losingPotAmount) / FEE_DIVISOR;
    uint256 operatorFee = (operatorFeeDecimal * losingPotAmount) / FEE_DIVISOR;
    creatorFees[token][creator] += creatorFee;
    operatorFees[token] += operatorFee;
    emit MarketsBetFeeCollected(marketCommitment, token, creator, creatorFee, operatorFee);
    losingPotAmount -= (creatorFee + operatorFee);
}
```

Above we see that the `creator` and `operator` fee are applied in real time whenever a bet is revealed. The result is that after the values are updated, the new fee percentages will be immediately applied to all revealed bets. This retroactively applies the updated fees to all bets even those for markets that closed well before the updated fees. To ensure fairness to all bettors, fees should be taken according to the percentage at the time of the bet.

## Recommendation
`creatorFeeDecimal` and `operatorFeeDecimal` should be cached upon market resolution and cached values should be read upon redemption rather than using the current values.
