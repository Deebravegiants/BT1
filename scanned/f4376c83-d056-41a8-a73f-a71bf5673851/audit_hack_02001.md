# [H] 7.2 Dynamic Weights Changing Problem

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security High Version 1 Code Corrected


Assume the pool has 10 X and 10 Y tokens that both have weight of 1. Initial invariant:

(^10) _X_ * (^10) _Y_ = 100
Now assume attacker sees an update in oracle price, that will change the weight of X tokens to 2.
Attacker performs a trade: in 990 Y, out 9.9 X. New constant product:
0. (^1) _X_ * (^1000) _Y_ = 100
After ChainLink price update, the X tokens weight become 2. New invariant:
( 0. (^1) _X_ )^2 * (^1000) _Y_ = 10
In 0.9 X, out 990 Y. The invariant holds:
New constant product:
( (^1) _X_ )^2 * (^10) _Y_ = 10
With 2 these trades that surround the price update, attacker profited by 9 X tokens.
The sandwiching can be performed using the Flashbots service. This issue is similar to the one that was
discovered in Curve.
Code corrected:
Swaap Labs introduced 2 solutions:
1.The relative difference between oracle price and pool price is capped:
AfterSwapPoolPrice/OraclePrice <= 102% + fee
2.If the user sells token that is in shortage, and the token price experienced increase in the current
block, extra fee is applied to compensate for a possible impermanent loss of the pool.
Together these 2 solutions help with the weight change sandwich attack.
