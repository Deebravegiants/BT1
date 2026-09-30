# [C] CALC-1 | boundMagnitude Fails To Bound Magnitude

## Summary
Severity: Critical
Contest weight: 0.2275
Dataset id: 19212
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When computing the sign of the resulting bounded value, the original value is divided by the
magnitude.
However the magnitude has already been adjusted to be within the min or max bounds, therefore
when the magnitude has been adjusted the resulting sign variable value is no longer a unit vector
indicating sign.
This results in the bounded value, in this case the nextSavedFundingFactorPerSecond, being in fact
unbounded.
For example:
value = 800
Min = 250
Max = 400
Magnitude is capped to 400
Sign = 800 / 400 = 2
The returned value is 400 * 800 / 400 = 800 which is outside of the deﬁned max
As a result, dynamic funding fees cannot be capped, leading to any market being entirely bricked
within hours of the dynamic funding fees being activated.

## Proof of Concept
https://github.com/GuardianAudits/GMX-Updates-9-4-23/blob/ad02d51629f0e3382d9052095d3f73f3d8faf49a/test/guardian/PoCs.ts#L26

## Recommendation
If the value is < 0 return -magnitude.toInt256() and if the value is >=0 return magnitude.toInt256()
