# [H] Revised Transfer Validation in EToken::transferFrom()

## Summary
Severity: High
Contest weight: 0.7864
Dataset id: 12007
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ERD protocol, EToken is a wrapped token contract that certifies users deposit of collaterals. The EToken balance of a user is the collateral amount of the user in the protocol. A user can transfer its EToken in normal mode, but must ensure that after the transfer the protocol is still in normal mode and its new ICR is greater than the CCR. While reviewing the validation of the transfer, we notice the logic issue that may permit a transfer that should be forbidden or block a transfer that should be permitted. To elaborate, we show below the related code snippet of the EToken::transferFrom() routine. At the beginning of the routine, it calls the _requireValidAdjustment() routine (line 105) to check whether the transfer is valid or not. However, in the _requireValidAdjustment() routine, we notice that it validates the trove for the msg.sender (line 115) while not the transfer _sender (line 100). As a result, a user can approve an operator to transfer all its EToken as long as the operator is valid for transfer. Based on this, we suggest to properly validate the trove of the transfer sender.
```solidity
function transferFrom(
    address _sender,
    address _recipient,
    uint256 _amount
) public virtual override(IERC20Upgradeable, ERC20Upgradeable) returns (bool) {
    uint256 share = getShare(_amount);
    _requireValidAdjustment(_amount);
    shares[_sender] = shares[_sender].sub(share);
    _totalShares = _totalShares.sub(share);
    super.transferFrom(_sender, _recipient, _amount);
    return true;
}

function _requireValidAdjustment(uint256 _amount) internal view {
    require(
        collateralManager.validAdjustment(
            msg.sender,
            tokenAddress,
            _amount
        ),
        "EToken: Invalid adjustment"
    );
}
```
What's more, in the _requireValidAdjustment() routine, it calls the collateralManager.validAdjustment() routine to validate for the transfer. While examining below the code of the CollateralManager::validAdjustment() routine, we notice it directly return false when the protocol is currently not in recovery mode (line 604). As a result, EToken transfer is forbidden in normal mode, though by design the transfer is permitted only in normal mode.
```solidity
function validAdjustment(
    address _account,
    address _collateral,
    uint256 _amount
) external view override returns (bool) {
    bool active = troveManager.getTroveStatus(_account) == 1;
    if (!active) return true;
    uint256 price = priceFeed.fetchPrice_view();
    uint256 totalDebt = getEntireSystemDebt();
    (, uint256 totalValue) = getEntireSystemColl(price);
    bool isRecoveryMode = _checkRecoveryMode(totalValue, totalDebt, CCR);
    if (!isRecoveryMode) return false;
    ...
    return newTCR >= CCR;
}
```

## Recommendation
Properly validate the trove of the transfer sender in the EToken::transferFrom() routine and allow the transfer in normal mode only.
