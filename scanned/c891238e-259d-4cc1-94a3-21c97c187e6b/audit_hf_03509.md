# [M] CALC-2 | boundMagnitude Function Cannot Bound 0

## Summary
Severity: Medium
Contest weight: 0.0516
Dataset id: 19213
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a boundary‑condition error in a helper routine that is intended to enforce a minimum absolute magnitude on a signed numeric value. The routine computes a sign by dividing the input value by a magnitude constant and then multiplies the magnitude by that sign. When the input value is exactly zero, the division yields zero, the sign becomes zero, and the multiplication returns zero, ignoring the supplied minimum parameter. As a result the function returns 0 instead of the expected minimum (for example 10) with the appropriate sign. This occurs whenever the contract calls the bounding function with a zero value, which can happen during funding‑rate updates, interest calculations, or any logic that normalises a delta that may be zero. An attacker or a malformed transaction can trigger the zero path, causing the contract to record a zero adjustment where a non‑zero floor was required. The impact is that the protocol’s accounting may miss a mandatory minimum funding rate change, leading to under‑payment of traders, incorrect incentive distribution, or a drift in the economic model. From a user perspective the UI may show a funding rate of 0% when a minimum of 0.1% should be applied, causing confusion and potentially loss of expected earnings. The issue was discovered during a manual audit of the GMX update contract where the auditor noticed that the min argument was never used for a zero input. The bug is subtle because the function appears to work for all non‑zero inputs and the zero case does not raise an exception, so it can go unnoticed in normal testing. The proper fix is to add an explicit check for a zero input and return the supplied minimum with the correct sign, which can be derived from a boolean flag indicating the direction of the change (increase or decrease). This aligns the routine with the generic class of lower‑bound enforcement bugs where edge‑case values bypass validation logic. By correcting the boundary handling the protocol restores its guarantee that funding‑rate adjustments never fall below the configured floor, preserving economic integrity and user expectations.

## Recommendation
When the value is 0 return the min with a sign informed by a boolean parameter. When the
FundingRateChangeType is Increase, the sign of the resulting min value should be whichever
direction the increase is heading in.
