# [H] Overcharging of closing and trigger

## Summary
Severity: High
Contest weight: 0.6130
Dataset id: 8392
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
Currently, the calculation for closing and trigger fees applies a fixed 5% fee to
all non-MARKET_CLOSE orders. This fee should only apply to LIQ_CLOSE orders.
For TP_CLOSE and SL_CLOSE orders, the calculation should use the pair close
fee percentage and pair trigger order fee percentage, respectively. As a result,
TP_CLOSE and SL_CLOSE orders are being overcharged.
function processClosingFees(
    ITradingStorage.Trade memory _trade,
    uint256 _positionSizeCollateral,
    ITradingStorage.PendingOrderType _orderType
) external returns (ITradingCallbacks.Values memory values) {
    // 1. Calculate closing fees
    values.positionSizeCollateral = getPositionSizeCollateralBasis(
        _trade.collateralIndex,
        _trade.pairIndex,
        _positionSizeCollateral
    ); // Charge fees on max(min position size, trade position size)
    values.closingFeeCollateral = _orderType == ITradingStorage.PendingOr
        ? (values.positionSizeCollateral * _getMultiCollatDiamond
        ().pairCloseFeeP(_trade.pairIndex)) /
        100 /
        ConstantsUtils.P_10
        //(_trade.collateralAmount * 5) / 100; // @audit charge fixed 5% for non-M
        : (_trade.collateralAmount * 5) / 100;
    values.triggerFeeCollateral = _orderType == ITradingStorage.PendingOr
        ? (values.positionSizeCollateral * _getMultiCollatDiamond
        ().pairTriggerOrderFeeP(_trade.pairIndex)) /
        100 /
        ConstantsUtils.P_10
        : values.closingFeeCollateral; // @audit charge fixed 5% for
        // non-MARKET_CLOSE
```

## Recommendation
Revise the fee calculation logic to apply the pair close fee percentage and pair
trigger order fee percentage specifically for TP_CLOSE and SL_CLOSE orders,
while retaining the 5% fee for LIQ_CLOSE orders.
