# [M] Improper Pool Amount Accounting in Vault

## Summary
Severity: Medium
Contest weight: 0.4356
Dataset id: 12418
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LogX is a decentralised exchange for trading perpetuals with its core trading logic in the Vault contract. This Vault contract has the key accounting poolAmounts state to keep track of pool funds for LLP pricing. While analyzing various activities that may affect the pool amount, we notice an issue in the position liquidation functionality that does not properly update the pool amount. In the following, we show the code snippet from the liquidatePosition() routine. This routine itself is designed to liquidate an underwater position. We notice the pool amount adjustment differs on the computed marginFees. If marginFees<0, the liquidated position may have positive funding rate and the pool amount should be increased by both abs(marginFees) and the position collateral. Similarly, if marginFees>0, we need to either reward pool by adding position.collateral - uint(marginFees), or decrease pool amount by subtracting uint(marginFees)- position.collateral. The current adjustment only considers the pool-rewarding branch, not the pool-deduction branch.
```solidity
if(marginFees < 0){
    _increasePoolAmount(position.collateralToken, utils.usdToTokenMin(position.collateralToken, uint(abs(marginFees))));
} else {
    if (uint(marginFees) < position.collateral) {
        uint256 remainingCollateral = position.collateral - uint(marginFees);
        _increasePoolAmount(
            position.collateralToken,
            utils.usdToTokenMin(position.collateralToken, remainingCollateral)
        );
    }
}
```

## Recommendation
Revise the above routine to properly adjust the pool amount when a position is liquidated.
