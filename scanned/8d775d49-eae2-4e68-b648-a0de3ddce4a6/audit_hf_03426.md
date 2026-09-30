# [M] PU-1 | Inaccurate Price Impact Formula

## Summary
Severity: Medium
Contest weight: 0.1587
Dataset id: 18727
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The comment in the applyImpactFactor function states the following: We divide by 2 here to more easily translate liquidity into the appropriate impactFactor values. For example, if the impactExponentFactor is 2 and we want to have an impact of 0.1% for $2 million of difference we can set the impactFactor to be 0.1% / 2 million, in factor form that would be 0.001 / 2,000,000 * (10 ^ 30). However this additional divisor of 2 is redundant, especially in the given example. Consider the diffUsd of 2,000,000 and an impactExponentFactor of 2 (ignoring units): exponentValue = 2,000,000 * 2,000,000; impactFactor = 0.001 / 2,000,000. exponentValue * impactFactor = 2,000,000 * 2,000,000 * .001 / 2,000,000 / 2 = 2,000,000 * .001 / 2. Without the extra division by 2 we already have the result we're looking for, 2,000,000 * .001 = 2,000 since 2,000,000 and 1/2,000,000 cancelled the additional x2 introduced. This directly contradicts the example given in the applyImpactFactor function.

## Proof of Concept
https://github.com/GuardianAudits/GMX-4/blob/c120e3310cc777c9c99de2ac1912824eb1090f6e/test/guardian/PoCs.ts#L28

## Recommendation
Remove the redundant 1/2.
