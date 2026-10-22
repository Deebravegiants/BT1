# [C] C-01 | All Debt Is Forgiven

## Summary
Severity: Critical
Contest weight: 0.2190
Dataset id: 22071
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If payDebt is called with an amount that is larger than the existing debt, the function wipes all existing debt and then attempts to add the remaining amount as collateral to the account. if (self.debt < amount) {self.debt = 0; updateCollateralAmount(self, SNX_USD_MARKET_ID, (amount - self.debt).toInt());} The problem lies with setting self.debt to 0 before performing the collateral update. This results in the full amount being updated as collateral, and the previous debt was essentially repaid at no cost. By just repaying 1 additional wei of debt, a user will have his entire debt repaid and his collateral increased by the debt amount + 1 wei.

## Proof of Concept
https://github.com/GuardianAudits/perps-v3-2/blob/a47dbb63e0543dd10ec633dd0b90f35c1b64298a/markets/perps-market/test/integration/guardian/pocs/POC_PayDebtForFree.test.ts

## Recommendation
Update collateral amount first before setting debt to 0.
