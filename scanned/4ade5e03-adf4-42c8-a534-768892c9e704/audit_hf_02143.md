# [M] Timely Price Update in validAdjustment()

## Summary
Severity: Medium
Contest weight: 0.4600
Dataset id: 12009
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.3, the collateralManager.validAdjustment() routine is used to validate if a EToken transfer from the sender is permitted or not. The routine basically checks three conditions: 1) if the protocol is currently in normal mode (TCR >= CCR); 2) if the new ICR of the sender is larger than the MCR; 3) if the protocol can be in normal mode after the transfer. In the following, we show the code snippet of the CollateralManager::validAdjustment() routine. In order to calculate the TCR/ICR, there is a need to fetch the latest collaterals prices from the price oracle. However, it comes to our attention that it simply fetch the last good prices from the priceFeed (line 599). The last good price is stored in the priceFeed for each collateral when the price is successfully obtained from the oracle. As a result, the last good price may be out of date without an initiative price update request to the oracle. Based on this, we suggest to update the prices via the priceFeed for all collaterals before using the last good prices.
```solidity
function validAdjustment(
    address _account,
    address _collateral,
    uint256 _amount
) public external view override returns (bool) {
    bool active = troveManager.getTroveStatus(_account) == 1;
    if (!active) {
        return true;
    }
    uint256 price = priceFeed.fetchPrice_view();
    uint256 totalDebt = getEntireSystemDebt();
    (, , uint256 totalValue) = getEntireSystemColl(price);
    bool isRecoveryMode = _checkRecoveryMode(totalValue, totalDebt, CCR);
    if (!isRecoveryMode) {
        return false;
    }
    (uint256[] memory colls, , ) = getTroveColls(_account);
    uint256 debt = troveManager.getTroveDebt(_account);
    (uint256 currValue, ) = getValue(collateralSupport, colls, price);
    uint256 value = _calcValue(_collateral, _amount, price);
    uint256 newICR = ERDMath._computeCR(currValue.sub(value), debt);
    if (newICR < MCR) {
        return false;
    }
    uint256 newTCR = ERDMath._computeCR(totalValue.sub(value), totalDebt);
    return newTCR >= CCR;
}
```
Note this issue is also applicable to the CollateralManager::getTotalValue()/TroveManagerRedemptions.updateTroves()/BorrowerWrappersScript::_getNetEUSDAmount(), etc.

## Recommendation
Revisit all the routines that fetch the last good prices add ensure the prices are updated to date.
