# [H] Inconsistent usage of `applyInterest`

## Summary
Severity: High
Contest weight: 0.1574
Dataset id: 231
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is unclear if the function `applyInterest` is supposed to return a new balance with the interest applied or only the accrued interest? There are various usages of it, some calls add the return value to the old amount:

    return
    bond.amount +
    applyInterest(bond.amount, cumulativeYield, yieldQuotientFP);
    and some not:

    balanceWithInterest = applyInterest(
    balance,
    yA.accumulatorFP,
    yieldQuotientFP
    );

This makes the code misbehave and return the wrong values for the balance and accrued interest.

Recommend making it consistent in all cases when calling this function.

## Recommendation
No recommendation
