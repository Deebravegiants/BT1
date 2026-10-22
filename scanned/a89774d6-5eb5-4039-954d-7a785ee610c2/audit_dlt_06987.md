# [M] M-07 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-angle-mitigation
Published: 2023-07-18
Source: https://github.com/code-423n4/2023-07-angle-mitigation-findings/issues/5
Type: code-finding

## Details
# Lines of code




# Vulnerability details

The fix addresses the scenarios when collaterals are removed between the crafting of the `minAmountsOut` list and the submission of the transaction. Then, we will have `amounts.length > minAmountOuts.length`, meaning that the following line causes a revert:
```solidity
        if (amountsLength != minAmountOuts.length) revert InvalidLengths();
```

However, as mentioned in the issue, only checking the length does not mitigate the issue fully. If one collateral is removed and another one added, it still exists. For instance, we could have:
- Initial collateral list [A, B, C, D]. This is used by the user to craft `minAmountOuts`
- Then, collateral A is removed, resulting in [D, B, C].
- Then, a new collateral Z is added, resulting in [D, B, C, Z].

We have `amountsLength == minAmountOuts.length`, therefore the transaction does not revert. However, the `minAmount` that the user passed in for A is now applied to the redemption of D.

To be fair, this scenario is extremely unlikely, but I would still say that the issue is technically not fixed completely.
