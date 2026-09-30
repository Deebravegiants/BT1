# [M] Liquidation might occur in- stantly after withdrawing max possible margin

## Summary
Severity: Medium
Reporter: jokr
Contest weight: 0.2452
Dataset id: 1790
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An incorrect position health check after withdrawing margin could lead to the position becoming liquidatable immediately after the withdrawal. The trader can withdraw margin up to an amount such that the effective position, after accounting for PnL, should be greater than 20% of the collateral. This ensures the position still has a 5% buffer to avoid reaching the liquidation state after withdrawing the maximum possible margin. require((int(_trade.initialPosToken) + pnl) > (int(_trade.initialPosToken) * int(100 - _WITHDRAW_THRESHOLD_P)) / 100, "W_T_B"); ,→ However, this check fails in cases where the trader has loss protection. Since the PnL used in the above check is the loss-protected PnL, the trader is able to withdraw more margin than intended based on the loss protection. But because the PnL used in the liquidation check does not consider loss protection, if the trader withdraws the maximum possible margin, their position will enter a liquidatable state immediately after the withdrawal. • In TradingCallbacks:85 margin withdrawal health check uses lossProtectedPnl, inflating position value and allowing excessive collateral than intended withdrawal while appearing healthy but actually not based on the liquidation price Internal pre-conditions 1. Trader should have pnl protection External pre-conditions 1. Trader should withdraw margin from open trade Attack Path The trader opens a long position with the following parameters: Collateral = 250 USDC Leverage = 4x LevPositionToken = 1000 Loss protection rebate = 20% The price then drops by 9%, reducing the price to 910 USDC. profitP = -9% * 4 = -36% pnl = -36% of 250 = -90 USDC net position value = 250 - 90 = 160 So the position remains in a healthy state. Next, the trader tries to withdraw 150 USDC from the margin. newCollateral = 100 USDC newLeverage = 10x profitP = -9% * 10 = -90% pnl = -90% of 100 = -90 USDC lossProtectedPnl = -72 USDC (20% loss protection rebate applied) net position value = initialPosToken - lossProtectedPnl = 28 In this case, the health check passes since 28 is greater than 20% newCollateral. The withdrawal is successful. However, on checking if the account is liquidatable: profitP = -90% pnl = -90% of 100 = -90 USDC net position value = 100 - 90 = 10 The position is now liquidated immediately because the net position value is less than 15% of the collateral. The health check does not work as intended in cases with loss protection, leading to traders potentially being liquidated after withdrawing margin.

## Recommendation
Consider using pnl instead on loss protected pnl in the health check
