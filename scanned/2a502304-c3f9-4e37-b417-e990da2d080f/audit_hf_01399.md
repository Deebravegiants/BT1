# [M] M-4 CONTROLLER.total_debt() may not be up to date

## Summary
Severity: Medium
Contest weight: 0.3891
Dataset id: 7174
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• AggMonetaryPolicy2.vy#L171
The MainController.updaterate() calls the monetary policy rate calculation method which may use a not updated total_debt().
For example, in the adjustloan() method the updaterate() is called before the total_debt update (MainController.vy#L781):
```solidity
debt_adjustment: int256 = MarketOperator(market).adjustloan(account, coll_change, debt_change_final, max_active_band)
self.updaterate(market, c.amm, c.mpidx) // self.total_debt is not updated
total_debt: uint256 = self.uintplusint(self.total_debt, debt_adjustment)
self.total_debt = total_debt
```
In case of large differences, AggMonetaryPolicy2 may not calculate the new rate correctly.

## Recommendation
We recommend calling self.updaterate() after updating the MainController.total_debt.
