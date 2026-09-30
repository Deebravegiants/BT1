# [M] M-04 | Interest Free Credits Intra-Day

## Summary
Severity: Medium
Contest weight: 0.0963
Dataset id: 21470
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The getTimeslot function returns the unix timestamp at the end of the day as today, and this is used while calculating daily interests during credit borrowing.
For example, when the current time is 14:05:00, today is considered as 23:59:59. Because of today is considered as the end of the day, the time between 23:59:59 and the exact borrow time are interest free.
If a user gets a credit on June 1st at 00:00:01 for only 1 day:
- Today is June 1st 23:59:59
- Credit end time is June 2nd 23:59:59
User will basically get 2 days credit by paying only 1 day interest.

## Recommendation
Consider adding a day to the newExpiry_ when first initializing a loan to account for the remainder of the current day. Otherwise, clearly document this behavior to users.
