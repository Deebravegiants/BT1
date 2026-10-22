# [M] MKT-1 | User Can Avoid Accrued Interest

## Summary
Severity: Medium
Contest weight: 0.1641
Dataset id: 19561
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Ambit protocol supports the usage of a DiscountModel to decrease the interest accrued on a user’s borrow position. Once the DiscountModel is set, the interest is calculated with the function calculateDiscountedLiabilities instead of the typical interest calculation. With the model a user can receive a discount for their entire borrow amount: Math.min(userLiability.borrowed, points * AMOUNT_PER_POINT).toUint128(); A user may be in the market for a prolonged period of time while there is no discount campaign and the marketState.borrowIndex will largely increase during that elapsed time. In order to avoid paying that interest, a user can wait to accrueLiabilities until a discount model is set. A user can burn Ambit to immediately increase their points such that the discount matches the borrow position, although this may require a large amount of Ambit. Afterwards the user will call function accrueLiabilities where the resultant interest will be zero, and the user will avoid the interest that they would have had to pay otherwise.

## Recommendation
Be extremely cautious with the discounts in the DiscountModel to prevent users from creating interest-free borrow positions. Furthermore, accrue liabilities for the user prior to burning Ambit.
