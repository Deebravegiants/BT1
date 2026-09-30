# [M] Incorrect calculations in the

## Summary
Severity: Medium
Contest weight: 0.2464
Dataset id: 1771
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An incorrect divisor is used in the deviation calculation when the Chainlink backup price is less than the Pyth price. This can result in unintended reverts even when the price is within the allowed deviation.
The issue stems from using bkPrice as the divisor in the if(bkPrice<price) case (here), whereas the correct divisor should be price. This causes the deviation to be calculated from bkPrice instead of from the intended price.
Internal pre-conditions
1. The pair in addition to Pyth is using a Chainlink backup feed.
2. The backup maxDeviation is set to 2% (or any other valid value).
External pre-conditions
None.
Attack Path
1. A transaction is executed for a pair that is using the Chainlink backup feed.
2. The Chainlink reported price is approximately -2% from the Pyth price.
3. The transaction is incorrectly reverted in a situation where it should be accepted.
• Reverting time-sensitive function.
• Loss of fees, as the system may subsequently decide to cancelPendingMarketOrder(). In case it was a market order.

## Proof of Concept
Consider a simple calculation with a BTC price of 50,000 and a 2% backup deviation.
This deviation allows an acceptable range of 49,000 to 51,000.
Currently, if Pyth reports a price of 50,000 and the Chainlink backup feed is 49,000, this should be within the acceptable deviation, and the transaction should proceed.
However, due to the incorrect divisor, the transaction is reverted as follows:
(50000 - 49000) * 100 / 49000 > 2%
(50000 * 10**10 - 49000 * 10**10) * 100 * 10**10 / (49000 * 10**10) = 20408163265 > 2%
Using the correct price divisor would yield the intended 2%:
(50000 * 10**10 - 49000 * 10**10) * 100 * 10**10 / (50000 * 10**10) = 20000000000

## Recommendation
Use price as the divisor in the if(bkPrice<price) case.
