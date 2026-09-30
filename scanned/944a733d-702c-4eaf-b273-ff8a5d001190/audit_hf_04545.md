# [M] M-05 | Order Fee Calculation Uses The Wrong Price

## Summary
Severity: Medium
Contest weight: 0.1058
Dataset id: 22110
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• The fillPrice is used in the calculateOrderFee function to calculate the notional.
• As the orderFee is a percentage taken from the notional a higher fillPrice will lead to a higher
orderFee and a lower fillPrice will lead to a lower orderFee.
This impacts long trades correctly, but short trades wrong:
• Long Trade:
• With a positive price impact the fillPrice decreases
• With a negative price impact the fillPrice increases
• Short Trade:
• With a positive price impact the fillPrice increases
• With a negative price impact the fillPrice decreases
Therefore a positive price impact on a short (trader balances the OI) increases the fillPrice and
therefore also the orderFee of the trader and vice versa.

## Recommendation
Use the orderPrice instead of the fillPrice.
