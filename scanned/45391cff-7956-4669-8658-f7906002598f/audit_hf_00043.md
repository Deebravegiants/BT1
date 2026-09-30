# [H] DIEMT-2 | vegaDifference Fee Not Valued At The Asset Price

## Summary
Severity: High
Contest weight: 0.1507
Dataset id: 119
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _calculateFee function, the feeTaken is incremented by the vegaDifference factored with the VEGA_MAKER_FACTOR or VEGA_TAKER_FACTOR. However the vegaDifference is not valued at the underlying asset price with Oracle.getValuePriced like the deltaDifference is. Therefore the additional fees from the vegaDifference are negligible. Because of this, the effect that the action has on the amm’s net vega exposure is not accounted for in the calculated fees and the fees are significantly cheaper than intended.

## Recommendation
Calculate the fees from the vegaDifference with Oracle.getValuePriced(vegaDifference.mulDivUp(MakerTakerFactors[_asset].VEGA_MAKER_FACTOR, 1e18), _asset).
