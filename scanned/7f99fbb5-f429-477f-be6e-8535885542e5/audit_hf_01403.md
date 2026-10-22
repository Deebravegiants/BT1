# [M] M-3 Hooks may result in user debt exceeding the globalmarketdebt_ceiling

## Summary
Severity: Medium
Contest weight: 0.5867
Dataset id: 7194
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• MainController.vy#L718
• MainController.vy#L768-L794
If a user creates a loan and the hook returns a negative value, then minted > debt_increase and unbacked stablecoins will be minted and not accounted in assertbelowdebtceiling(total_debt):
```solidity
def create_loan(
    ...
    debt_amount: uint256,
    ...
):
    ...
    hook_adjust: int256 = self.call_hooks(
        ...
    )
    debt_amount_final: uint256 = self.uintplusint(debt_amount, hook_adjust)
    ...
    debt_increase: uint256 = MarketOperator(market).createloan(account, coll_amount, debt_amount_final, nbands)
    total_debt: uint256 = self.total_debt + debt_increase
    self.assertbelowdebtceiling(total_debt)
    self.total_debt = total_debt
    self.minted += debt_amount
```
MainController.vy#L718
In another scenario, if a user provides a negative debt_change to the adjustloan() and the hook adjusts it to a positive value, then the original debt_change < 0 but debt_adjustment > 0. In that case the total_debt is increased, but we don't fall into the if debt_change > 0 statement and do not check for the debt ceiling:
```solidity
debt_change_final: int256 = self.call_hooks(...) + debt_change
...
debt_adjustment: int256 = MarketOperator(market).adjustloan(account, coll_change, debt_change_final, max_active_band)
...
total_debt: uint256 = self.uintplusint(self.total_debt, debt_adjustment)
if debt_change != 0:
    debt_change_abs: uint256 = convert(abs(debt_change), uint256)
    if debt_change > 0:
        self.assertbelowdebtceiling(total_debt)
        self.minted += debt_change_abs
    STABLECOIN.mint(msg.sender, debt_change_abs)
    else:
        self.redeemed += debt_change_abs
    STABLECOIN.burn(msg.sender, debt_change_abs)
```
MainController.vy#L768-L794

## Recommendation
We recommend checking the total_debt against the debt ceiling when the debt_adjustment > 0 in the adjust_loan() function. We also recommend taking into account stablecoins which are not included in the total_debt and are not backed.
