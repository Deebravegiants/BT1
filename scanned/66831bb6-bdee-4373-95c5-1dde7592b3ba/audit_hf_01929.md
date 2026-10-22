# [H] Market interest is not always accrued

## Summary
Severity: High
Contest weight: 0.5513
Dataset id: 10559
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
The market accrues interest, which changes totalAssets() in theLoopStrategy. Thus, everytime there is some action that modifies the amount of assets, interest should always be accrued first. However, markets.accrueInterest() in only called on _withdraw(), post shares/assets calculation, which will lead to an incorrect asset withdrawal.
On deposit/mint, it also does not accrue market interest before calculating the shares to receive.
In the view functions, such as totalAssets(), expectedAmountsToWithdraw() or maxWithdraw(), it also does not consider the accrued interest from the market.
```

## Recommendation
Accrue market interest before each action and ideally find a way to fetch the accrued interest in a view function (the market does not seem to have this ability currently).
