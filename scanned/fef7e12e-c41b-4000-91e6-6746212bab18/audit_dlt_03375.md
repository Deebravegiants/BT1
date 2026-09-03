# [M] Flashloan griefing attack

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-yield
Published: 2021-06-01
Source: https://github.com/code-423n4/2021-05-yield-findings/issues/27
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

Funds from contracts that approved a join and implement the flashloan interface can be stolen.
One can call `Join.flashLoan(vulnerable_contract, token, amount)` and the contract's balance will be decreased by the fees they have to pay for the flashloan. One can repeat this until the contract's balance is emptied.

## Impact
Funds from contracts that approved a join and implement the flashloan interface can be "burned".

## Recommended Mitigation Steps
Don't allow taking flashloans on behalf of another account, or don't allow join to `transferFrom`, i.e., let the receiver explicitly push the funds.
