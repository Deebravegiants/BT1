# [C] GLOBAL-4 | positionIncreasedAtBlock Used To Game Orders

## Summary
Severity: Critical
Contest weight: 0.2448
Dataset id: 18198
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LimitIncrease, LimitDecrease, and StopLossDecrease orders depend on the positionIncreasedAtBlock for the price ranges that they can be executed with. A malicious trader may take advantage of past prices by closing their position to reset the positionIncreasedAtBlock to 0. Consider the following attack: 1. A trader makes two LimitIncrease orders with the same triggerPrice. 2. The first one is successfully executed and the positionIncreasedAtBlock is set to 100. 3. The second one is not executed since the valid descending price range is from before the positionIncreasedAtBlock. 4. The trader waits and observes that price moves in their favor, and then closes their position with a MarketDecrease order. Therefore resetting the positionIncreasedAtBlock to 0. 5. Now the second LimitIncrease is able to be executed with the out of date price range, enabling a risk-free trade.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/GLOBAL_4.ts

## Recommendation
Track when the position was closed and add this block number to the validation for LimitIncrease, LimitDecrease, and StopLossDecrease orders so that they cannot be used to abuse past prices.
