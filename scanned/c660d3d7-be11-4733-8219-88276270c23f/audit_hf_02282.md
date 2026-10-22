# [M] Twav._getTwav

## Summary
Severity: Medium
Contest weight: 0.3942
Dataset id: 12482
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the internal helper function that calculates the time‑weighted average valuation (TWAV) for the vault. The function uses a conditional check that examines the stored timestamp of the most recent observation. Because the timestamp value is stored modulo 2**32, it can wrap to zero after a sufficiently long period or under certain edge‑case inputs, even when the observation buffer already contains the required number of entries. When the timestamp equals zero, the condition evaluates to false and the function immediately returns a zero TWAV instead of the correct aggregated value. This erroneous zero propagates to the main public functions that rely on the TWAV, namely the buy and sell operations of the vault. As a result, a user attempting to purchase tokens may receive an unexpectedly high amount (potentially for free) or a user trying to sell may receive nothing, breaking the protocol’s accounting invariants and exposing the vault to economic loss. The flaw occurs only when the timestamp wraps, a scenario that is rarely exercised in typical test suites, making it difficult to notice during standard development. It was discovered through manual code review during a third‑party audit, where the reviewer noticed that the conditional logic did not account for the modular nature of the timestamp field. The root cause is the reliance on a mutable, wrap‑around field to signal that enough observations have been recorded, instead of a monotonic accumulator such as the cumulative valuation, which never resets. To remediate the issue, the conditional should be rewritten to verify that the cumulative valuation of the latest observation is non‑zero (or that a sufficient count of observations has been stored) before proceeding with the TWAV calculation. Additionally, the implementation should explicitly handle the case where the timestamp wraps, ensuring that a zero value is never returned unintentionally. By correcting the guard condition and adding proper edge‑case handling, the vault will maintain correct price calculations, preserve user expectations (users expect to receive a fair amount of tokens when buying or selling), and uphold the protocol’s financial integrity.

## Proof of Concept
I think this condition is to confirm at least 4 values were saved for twav calculation.

Btw this timestamp would be zero even though there are more than 4 values properly as it’s modularized by 2**32.

In this case, the if condition will be false and this function will return 0.

## Recommendation
I see “cumulativeValuation” is increasing all the time and recommend replacing “timestamp” with “cumulativeValuation”.

```solidity
if (twavObservations[TWAV_BLOCK_NUMBERS - 1].cumulativeValuation != 0) {
```

Interesting catch. This is related to [#178](https://github.com/code-423n4/2022-06-nibbl-findings/issues/178) but presents a distinct issue.
