# [C] Liquidators Can Manipulate Pool’s Proﬁt or Loss Values

## Summary
Severity: Critical
Contest weight: 0.2231
Dataset id: 14303
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Liquidators can manipulate the protocol’s proﬁt and loss accounting in
CreditFacade.liquidateCreditAccount(),
which can lead to theft of funds from the pool.
The call to _multicall() is done after totalValue is calculated. Hence, if a liquidator borrows additional funds
before closing the target credit account, totalValue will be under-represented in comparison to
borrowedAmountWithInterest.
This causes CreditManager._calcClosePaymentsPure() to miscalculate the loss amount as
amountToPool >= totalFunds, which means amountToPool = totalFunds. The totalFunds will be less than
borrowedAmountWithInterest, therefore the loss amount will be calculated as
borrowedAmountWithInterest - amountToPool.
This vulnerability allows an attacker to continually burn diesel tokens held by the treasury at no cost to the attacker.
The attacker can recover the tokens that they added to the borrower account.

## Recommendation
Alter the logic of CreditManager._calcCLosePaymentsPure() to reliably compute correct payment amounts in the
case of liquidations.
