# [H] 6.1 Waterfall Miscalculation

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

The value of a tranche can be updated by anyone by calling
StructuredPortfolio.updateCheckpoints. We expect the following property to hold:

```
Executing updateCheckpoints consecutively in one block (with no other transactions in between)
should not change the checkpoints since no time has passed and the value of the portfolio has not
been changed.
```
However, this property does not hold. To showcase that, we need to consider how the waterfall is
calculated.

The waterfall is calculated by using each tranche's checkpoints and adding the deficit of a tranche to it.
This is considered the total assumed value of the tranche. This means that if we would call
updateCheckpoints multiple times, the deficit of a tranche would be added up again on every
calculation of the waterfall.


Normally, however, this is not the case since the resulting waterfall values are bound by the total value of
the portfolio (virtual token balance + loans value) that hasn't been used by the less risky tranches.
Therefore, we assume the following property:

```
If a tranche has a deficit > 0, all riskier tranches (i.e., all tranches with a lower waterfall index) have a
value of exactly 0.
```
In practice, this assumption does not hold as can be seen in the following example (assuming no fees
and no compounding for simplification):

- The senior tranche has a 1% interest.
- The junior tranche has a 2% interest.
- Each tranche holds a value of 100 tokens.
- Two loans are issued:
    - Loan A: 102 tokens with 0% interest.
    - Loan B: 180 tokens with 10% interest.
- Loan A defaults.
- A deficit of 2 tokens is added to the junior tranche and the equity tranche now holds 0 value.
- After one year, the total assets of the portfolio is 216 (18 tokens in balance + 180 tokens in principal
    of open loans + 18 tokens in interest).
- The Senior tranche should hold 101 tokens.
- The Junior tranche should hold 102 tokens but still has a deficit of 2 tokens.
- The equity tranche is assigned 13 tokens.

This violates the assumed property. We can now call StructuredPortfolio.updateCheckpoints
multiple times and add up the deficit of 2 tokens, until the value of the junior tranche is 115 and the value
of the equity tranche is 0. After 1 year, the junior tranche has now accrued 15% interest while it should
have accrued 2%. In other words, calling the StructuredPortfolio.updateCheckpoints
consecutively changes the value of the tranches.

Code corrected:

If some loan in a portfolio has defaulted, StructuredPortfolio.updateCheckpoints subtracts the
delta of the previous and the updated value of a tranche from the tranche's deficit. This allows the deficit
to be settled with accrued interest, fixing the described problem.
