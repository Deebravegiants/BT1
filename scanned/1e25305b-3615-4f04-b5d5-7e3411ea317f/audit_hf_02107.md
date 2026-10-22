# [M] Inconsistent Handling in Pool::trimExtraToTreasury()

## Summary
Severity: Medium
Contest weight: 0.4600
Dataset id: 11864
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Pool contract provides a public trimExtraToTreasury() function to transfer extra collaterals[0]/dark/share assets from reserve to profitSharingFund_. Our analysis with this routine shows the current value assigned to the temporary variable _mainCollateralBal is inconsistent with the variable definition. To elaborate, we show below its code snippet. Specifically, the value assigned to the temporary variable _mainCollateralBal should be _treasury.globalCollateralBalance(0), instead of current _treasury.globalCollateralValue(0).div(10 ** missing_decimals[0]) (line 669).
```solidity
function trimExtraToTreasury() public returns (uint256 _collateralAmount, uint256 _darkAmount, uint256 _shareAmount) {
    uint256 _collateral_price = getCollateralPrice(0);
    uint256 _total_dollar_FullValue = IERC20(dollar).totalSupply().mul(_collateral_price).div(PRICE_PRECISION);
    ITreasury _treasury = ITreasury(treasury);
    uint256 _totalCollateralValue = _treasury.globalCollateralTotalValue();
    uint256 _dark_bal = _treasury.globalDarkBalance();
    uint256 _share_bal = _treasury.globalShareBalance();
    address _profitSharingFund = _treasury.profitSharingFund();
    if (_totalCollateralValue > _total_dollar_FullValue) {
        _collateralAmount = _totalCollateralValue.sub(_total_dollar_FullValue).div(10 ** missing_decimals[0]).mul(PRICE_PRECISION).div(_collateral_price);
        if (_collateralAmount > 0) {
            uint256 _mainCollateralBal = _treasury.globalCollateralValue(0).div(10 ** missing_decimals[0]);
            if (_collateralAmount > _mainCollateralBal) _collateralAmount = _mainCollateralBal;
            _requestTransferFromReserve(collaterals[0], _profitSharingFund, _collateralAmount);
        }
        if (_dark_bal > 0) {
            _darkAmount = _dark_bal;
            _requestTransferFromReserve(dark, _profitSharingFund, _darkAmount);
        }
        if (_share_bal > 0) {
            _shareAmount = _share_bal;
            _requestTransferFromReserve(share, _profitSharingFund, _shareAmount);
        }
    } else {
```

## Recommendation
Assign the correct value to the variable _mainCollateralBal (line 669) for above mentioned function.
