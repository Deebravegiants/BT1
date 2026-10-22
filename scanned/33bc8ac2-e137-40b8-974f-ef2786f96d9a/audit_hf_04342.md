# [H] H-03 | Interest Free Borrowing Due To TimeslotLib

## Summary
Severity: High
Contest weight: 0.2379
Dataset id: 21498
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can borrow reserves from CreditFacility using bAssets as collateral. A small interest will be paid based on the credit amount and the days added. The issue arises when users borrow more reserves with an existing credit account, without adding more days to expiry time. The protocol will try to calculate the interestOnNewCollateral based on the daysRemaining, but this value is 0 as there won't be any days remaining during the last expiry day. Any user borrowing during the last expiry day of the account, and does not add more days to the expiration, will effectively pay no interest for the new credit. Users might take advantage of this issue, by borrowing reserves from the FLOOR and ANCHOR, and repaying them in the same transaction to the FLOOR, and only pay gas fees. This will cause the capacity to be increased at will, as well as reduce the ANCHOR reserves that support the current price, opening the opportunity for arbitrageurs to extract reserves from the protocol.

## Recommendation
Prevent users from borrowing more credit during the last day of expiry if they are not adding more days to account expiration.
