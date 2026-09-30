# [H] H-12 | Vault Liquidated By Malicious Depositor

## Summary
Severity: High
Contest weight: 0.2231
Dataset id: 21971
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious actor may observe that Gamma currently has a high leverage and intentionally push this leverage up to force the PerpetualVault position to be liquidated. A user may do this by creating large deposits and then initiating withdrawals for those deposits as soon as possible to levy the MarketDecrease order position fee on the vault position. Users do not pay for the MarketDecrease order position fee and thus this fee is deducted from the remaining position thus changing the leverage of the remaining position. Once this has been repeated several times the vault position will have a very high leverage which makes it liquidatable almost instantaneously. The malicious actor can profit off of this liquidation by setting a limit order which can only be triggered once the liquidation has occurred and the priceImpact allows for immediate profit.

## Recommendation
Adjust the initialCollateralDelta amount for the Position fees that will be experienced for the MarketDecrease order. This way the withdrawer takes on the burden of the fee and the vault position leverage cannot be manipulated.
