# [C] Funding Rate Manipulation #2

## Summary
Severity: Critical
Contest weight: 0.3804
Dataset id: 14671
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The funding rate is a time-weighted average difference between the oracle price and the market price. Users
are either rewarded or taxed based on whether the oracle price is above or below the market price and whether
they are long or short.
Users are able to manipulate their funding rate index to potentially earn themselves rewards and/or avoid paying
fees.
The funding rate will be applied to a trade after the base and quote have been adjusted for the trade as:
base = base −(currentGlobalRate −currentUserRate) ∗quote
Consider the following example where:
• currentGlobalRate > 0
• user1 and user2 have currentUserRatei = 0
The following steps can be used in increase a users base.
1. user1 and user2 both deposit amount di respectively,
2. user1 makes a trade of negligible size (or trades with themselves) such that currentUserRate1 = currentGlobalRate
3. trade1 : {price1, amount1, longUser : user1, shortUser : user2}
Since currentUserRate1 = currentGlobalRate:
user1 : base = d1 −amount1 ∗price1 −(currentGlobalRate −currentUserRate1) ∗amount1
= d1 −amount1 ∗price1
Since user2 was short the quote will be negative the amount of the trade and currentUserRate2 = 0
hence:
user2 : base = d2 + amount1 ∗price1 −(currentGlobalRate −currentUserRate2) ∗(−amount1)
= d2 + amount1 ∗price1 + currentGlobalRate ∗amount1
Both user will now have currentUserRate = currentGlobalRate.
Tracer Protocol
4. We now close the position through trade2 : {price1, amount1, longUser : user2, shortUser : user1}
which gives us
user1 : base = d1
user2 : base = d2 + currentGlobalRate ∗amount1
This attack can be applied if currentGlobalRate < 0 by switching the long and short users in steps three (3) and
four (4).
The impact of this attack is that users are able to artificially increase their base. By creating numerous accounts
and applying this attack multiple times an attacker would be able to withdraw all of the funds in the protocol.

## Recommendation
The funding rate needs to ensure that the net impact on the sum of user’s base is zero. One method for doing
this is applying the global rate directly to the amount in the trade without using user specific rates or user specific
quotes, this will ensure that the change in base of both users will be the same absolute value but opposite in
sign.
Tracer Protocol
