# [H] ORDU-1 | Referral Code Manipulation

## Summary
Severity: High
Contest weight: 0.2227
Dataset id: 18514
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious user can manipulate the referral code associated with their account to decide whether
or not a trade should be executed.
For example, the referral code could be switched to a higher discount just in time to allow a
MarketIncrease execution tx to pass the order.minOutputAmount() validation and go through.
This allows a malicious trader to make a short-term risk-free trade as they can decide whether or not
they should be executed successfully with prices from a few blocks ago.
Additionally, the customDiscountShare of a single discount code could be leveraged in the same
way.
Notice that allowing the referral codes to be adjusted after orders are submitted also allows for
referrer manipulations. This way referrers can promise a 2% discount but front-run order executions
to adjust the customDiscountShare such that the trader receives no discount.

## Recommendation
Store the referral discount on a per-order basis. Do not allow the referral discount to be adjusted in
real-time by either the referral code being used or the customDiscountShare of a particular code.
