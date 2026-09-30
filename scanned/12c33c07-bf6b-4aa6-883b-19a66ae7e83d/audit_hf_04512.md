# [C] C-04 | Existing Debt Can Be Erased When Settling Order

## Summary
Severity: Critical
Contest weight: 0.1729
Dataset id: 22075
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function charge is called when orders are settled to perform collateral and debt accounting. The issue lies with the scenario where: 1) trader makes a loss, 2) leftover sUSD credit > 0 and 3) existing debt > 0. In that scenario, due to not accounting for existing debt, all debt is reset to 0. Consider this scenario:
• Trader A deposits ETH collateral, makes a losing trade and incurs debt
• Trader A deposits sUSD collateral, makes another losing trade and has previous debt erased

## Recommendation
In PerpsAccount.charge, account for existing debt as shown below: if (leftoverCredit > 0) { updateCollateralAmount(self, SNX_USD_MARKET_ID, amount); newDebt = self.debt; // insert this } Also, consider reducing any existing debt when traders deposit sUSD collateral.
