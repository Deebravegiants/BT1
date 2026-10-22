# [H] Ineffective Check in validateBorrow()

## Summary
Severity: High
Contest weight: 0.3050
Dataset id: 14349
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function validateBorrow() in ValidationLogic.sol is used to ensure that a user is allowed to perform a borrow. It verifies conditions such as, if the user has sufficient collateral to make a borrow.
There is an ineffective control statement on line [200], if (vars.rateMode == ReserveLogic.InterestRateMode.STABLE). This statement is ineffective as the variable vars.rateMode is never initialised and thus the check is equivalent to if (0 == 1) and so will never pass.
As a result the following requirements for stable borrowing are not validated:
• stable rate borrowing is enabled;
• the user has less collateral in the currency than borrow amount OR
• the borrow amount is less than 25% of the liquidity.
The impact is that users may make a stable borrow when it has not been enabled. If done on an asset that has not been configured to allow stable borrows then LendingRateOracle.getMarketBorrowRate(asset) would return zero. As a result, a user may borrow at a rate of 0%. See AAV-03 for further details on the impact of this vulnerability.
Users may also borrow a large percentage of the liquidity at a low rate and in the same currency as their collateral which would potentially allow them to earn more in revenue than they pay in fees by then depositing the borrowed funds. This is because both the stable and variable rate will be increased for future users.

## Recommendation
We recommend using the variable interestRateMode instead of vars.rateMode in the afore mentioned control statement.
interestRateMode is a parameter to the function which is initialised to the correct value, thereby correctly triggering the if statement.
