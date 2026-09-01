# [M] No discount with users with Referral Tier 3

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-buffer
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/101
Type: sherlock-finding

## Details
Ch_301

medium

# No discount with users with Referral Tier 3

## Summary
On **ReferralStorage.sol** The `referrerTier`, `referrerTierDiscount`and `referrerTierStep` has a problem because the length of  `referrerTierDiscount` and `referrerTierStep`

## Vulnerability Detail
On `BufferBinaryOptions._getSettlementFeeDiscount()`
```solidity
        if (referrer != user && referrer != address(0)) {
            uint8 step = referral.referrerTierStep(
                referral.referrerTier(referrer)
            );
```
The `referrerTier` is a mapping on **ReferralStorage.sol**
And `referrerTierStep` another mapping seated by `ReferralStorage.configure()`
```solidity
        for (uint8 i = 0; i < 3; i++) {
            referrerTierStep[i] = _referrerTierStep[i];
        }
```
So `referrerTierStep.lengh == 3` 

In case the user has `referrerTier == 0` that means he never create a Tier 1 code. 
but he still can get an x% discount. like he has a Tier 1 code 
Because `referral.referrerTierStep(0)` return a discount for Tier 1.

Now I’m not sure how the `referrerTier` will organize the Tiers, but in case the `referrer` is on Tier 1 and `referral.referrerTier(referrer)` return 0. that’s means 
Tier 1 ==> 0 
Tier 2 ==> 1
Tier 3 ==> 2
In this case, we have only the previously mentioned problem


but in case the `referrer` is on Tier 1 and `referral.referrerTier(referrer)` return 1.

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/101_
