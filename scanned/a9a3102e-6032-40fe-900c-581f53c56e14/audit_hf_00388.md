# [M] The closing fee is not factored

## Summary
Severity: Medium
Contest weight: 0.1339
Dataset id: 1774
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Based on Avantis documentation (docs) and general logic, the closing fee should be included in the liquidation price calculation, just as the rollover fee is. The documentation specifies:  
CollateralHealthRatio=(NetCollateral+PnL-accumulatedmarginfee-closingfee)/NetCollateral  
Omitting the closing fee deduction results in the getTradeLiquidationPrice() function calculating a liquidation price that is higher than it should be.  
The standard closing fee is not deducted in the getTradeLiquidationPricePure() function (here). This discrepancy with the documentation creates potential for inaccurate liquidation price ranges.  
Internal pre-conditions  
None.  
External pre-conditions  
None.  
Attack Path  
This is a straightforward calculation error.  
• Incorrect distribution between PnL and standard fees.  
• The tranches reserves and OI will be affected by the trade that should be already liquidated.

## Recommendation
Add the closing fee to the liquidation price calculation.
