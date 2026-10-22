# [M] ATPH-4 | DoS On Average Entry Price

## Summary
Severity: Medium
Contest weight: 0.1605
Dataset id: 19357
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a position is updated after a trade, the average entry price is calculated using calAverageEntryPrice. However, if the openingCost and currentHolding are of the same sign, the calculation of position.averageEntryPrice = halfDown16_8(-openingCost, currentHolding).toUint128() will revert with a SafeCastOverflow. This is because halfDown16_8(-openingCost, currentHolding) will return a negative int which cannot be cast to a uint. This can occur if the currentHolding exceeds the openingCost for a short position, because halfDown16_8 will round the quotient to -1 on else { quotient -= 1; }; Note that if halfDown16_8 is modified to round up on a 0 quotient, the issue can still occur if currentHolding exceeds the openingCost for a long position, because halfDown16_8 will round the quotient to 1 and the currentHolding is also positive.

## Proof of Concept
https://github.com/GuardianAudits/OrderlyEVMContractsSuite/blob/4e216c2befe63c5379059f9359a7b3a0da008a71/test/GuardianPOC.t.sol#L397C5-L501C6

## Recommendation
Carefully consider which markets are supported, as markets with small prices are more susceptible to this issue. Furthermore, consider implementing a minimum trade size since the attack is more susceptible to smaller quantities causing the openingCost to round down to -1.
