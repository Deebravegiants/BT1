# [H] 5.1.2 Liquidation might fail

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** OverlayV1Market.sol#L345-L376, Position.sol#L221-L
**Description:** Theliquidate()function checks if a position can be liquidated and vialiquidatable(), uses
maintenanceMarginFractionas a factor to determine if enough value is left. However, in the rest of theliqui-
date()functionliquidationFeeRateis used to determine the fee paid to the liquidator.
It is not necessarily true that enough value is left for the fee, as two different ways are used to calculate this which
means that positions might be liquidated.
This is classified as high risk because liquidation is an essential functionality of Overlay.
contract OverlayV1Market is IOverlayV1Market {
function liquidate(address owner, uint256 positionId) external {
...
require(pos.liquidatable(..., maintenanceMarginFraction),"OVLV1:!liquidatable");
...
uint256 liquidationFee = value.mulDown(liquidationFeeRate);
...
ovl.transfer(msg.sender, value - liquidationFee);
ovl.transfer(IOverlayV1Factory(factory).feeRecipient(), liquidationFee);
}
}
library Position {
function liquidatable(..., uint256 maintenanceMarginFraction) ... {
...
uint256 maintenanceMargin = posNotionalInitial.mulUp(maintenanceMarginFraction);
can_ = val < maintenanceMargin;
}
}


**Recommendation:** Also take into accountliquidationFeeto determine if a position can/should be liquidated.
Note: functionbuild()also callsliquidatable().
**Overlay** : Agreed. The way the liquidation fee amount is calculated, it’s taken from the remaining maintenance
margin once theliquidate()function is called (less any burn of margin as insurance).
So the liquidation fee in its current form is not as a percentage of the currentnotionalWithPnl()like trading fees
are, which means that it won’t affect the ability to liquidate the position. We should potentially change this.
Fixed in commit 082c6c7.
**Spearbit:** Acknowledged.
