# [H] LOTY-3 | Calling claimBoost Before Claiming Points Breaks The User's Boost

## Summary
Severity: High
Contest weight: 0.2861
Dataset id: 19577
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The UserPoints.boost is supposed to be at 10 (equating to 1x) but is 0 initially. When claimPoints() gets called after waiting for 2 EPOCHs the UserPoints.boost is set in the following snippet:
user.boost = user.boostOrDefault(); // @audit gets set from 0 to 10 here
The user can make their boost larger by calling claimBoost() if one is available to them. The current implementation of the system has a FirstLoanBoostModule which gives users an additional 0.1x on top of their 1x boost. The requirement for it is that they have borrowed more than 0 from the protocol and that they have a positive point balance through UserPoints.total(). The issue arises if the user burns AMBT with burnTokens() before calling claimPoints() to set their initial UserPoints.boost to 10 and then calls claimBoost(). This would set their boost to 0.1x instead of to 1x due to the following LoC:
user.boost = Math.min(user.boost + boost, LoyaltyLib.MAX_BOOST).toUint64();
Here UserPoints.boost is not yet set to the default boost, hence the user's boost for their balance1 becomes 10x smaller than it should be and causes them to lose out on 90% of the rewards they should be receiving.

## Recommendation
Consider implementing the following changes across the Loyalty.sol file:
1. Check whether the UserPoints.balance1 specifically is > 0 for boost eligibility.
2. Set the UserPoints.boost to UserPoints.boostOrDefault() in burnTokens() and supply().
