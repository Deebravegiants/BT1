# [M] fundLoan() can be DoSed if returnFunds() is called before it.

## Summary
Severity: Medium
Contest weight: 0.0869
Dataset id: 10265
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It’s possible to stop loans from being funded by calling returnFunds(). Exploit scenario ● attacker sees fundLoan(...) transaction and calls returnFunds(...) with an arbitrary amount ● returnFunds(...) increases _drawableFunds ● fundLoan(...) overrides _drawableFunds, which means that the amount sent earlier will be unaccounted ● the require that there are 0 unaccounted funds fails and the transaction reverts The lenders have incentive to do this if they want to withdraw and a loan would remove liquidity, see getRedeemableAmounts(...).

## Recommendation
In fundLoan(...), increase _drawableFunds instead of setting it.
