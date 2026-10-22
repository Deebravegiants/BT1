# [H] Liquidation might fail

## Summary
Severity: High
Contest weight: 0.5924
Dataset id: 11199
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The liquidate() function checks if a position can be liquidated and via liquidatable(), uses maintenanceMarginFraction as a factor to determine if enough value is left. However, in the rest of the liquidate() function liquidationFeeRate is used to determine the fee paid to the liquidator. It is not necessarily true that enough value is left for the fee, as two different ways are used to calculate this which means that positions might be liquidated. This is classified as high risk because liquidation is an essential functionality of Overlay.
```solidity
contract OverlayV1Market is IOverlayV1Market {
    function liquidate(address owner, uint256 positionId) external {
        ...
        require(pos.liquidatable(..., maintenanceMarginFraction), "OVLV1:!liquidatable");
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
```

## Recommendation
Also take into account liquidationFee to determine if a position can/should be liquidated.
