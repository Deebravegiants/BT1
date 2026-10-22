# [C] LOTY-2 | Total Points Does Not Match Sum Of User Points

## Summary
Severity: Critical
Contest weight: 0.3156
Dataset id: 19574
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user burns their Ambit, they are immediately credited with points that experience a 5x multiplier. However, if a user burns less than 1e7 of an Ambit, the total.points will not increment: total.points += LoyaltyLib.boostMul(amount.toUint64(), LoyaltyLib.BURN_BOOST); This is because in the boostMul function, the returned point value will be truncated to 0: points / POINT_DENOMINATOR * boost / DEFAULT_BOOST; A user could maliciously take advantage of this by initially burning more than 1e7 Ambit. This will be reflected in both the total and the user’s point balances as there will not be truncation. The user can then burn less than 1e7 Ambit which will not be reflected in the total of the Loyalty due to the truncation, but it will be reflected in the point balance of the user because the user’s balance2 is already above 1e7: points.balance2 / POINT_DENOMINATOR * BURN_BOOST / DEFAULT_BOOST; Because the total points are less than needed, the tokenReward.index will be larger which will inflate the rewards to be dispersed: tokenReward.index += ((amount * REWARDS_MULTIPLIER) / loyalty.getTotalPoints()).toUint128(); Users will not be able to claim their rewards as more reward tokens are attempted to be sent than actually exist in the contract. This can be repeatedly done by malicious users to widen the spread between the total points and sum of all users’ points.

## Recommendation
In function burnTokens, remove the user’s prior points from the total and add their new points with the boost similar to function updateBoost. Similarly adjust functions withdraw and claimPoints to avoid the discrepancy as well.
