# [M] `_updateTwav

## Summary
Severity: Medium
Contest weight: 0.5709
Dataset id: 12359
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an integer overflow in the cumulative valuation calculation used by the TWAV (time‑weighted average valuation) oracle. The contract stores a running total of valuation * time elapsed (cumulativeValuation) and later derives the average by subtracting two consecutive cumulative values and dividing by the elapsed time. Solidity 0.8+ automatically reverts on overflow unless the operation is placed inside an unchecked block. In both the _updateTwav function and the _getTwav helper the code adds the product of the current valuation and the time elapsed to the previous cumulative valuation without an unchecked safeguard. When the product or the sum exceeds the maximum value representable by uint256, the addition overflows, causing a transaction revert and breaking the oracle logic. An attacker or any user can trigger the overflow by supplying an excessively large valuation or by repeatedly calling updateTWAV so that the cumulative total grows past the uint256 limit. Once the overflow occurs the contract cannot record new observations, the TWAV calculation reverts, and any downstream logic that depends on a valid price feed – such as fee calculations, collateral valuations, or user refunds – fails. From a user’s perspective a transaction that updates the price may simply revert, balances may appear unchanged, or a user may receive a zero refund because the price feed returns an invalid value. The issue was discovered during a Code4rena audit where the auditors examined the arithmetic of the TWAV implementation and identified that the cumulative sum was not protected against overflow. The bug is subtle because the code comments suggest that “cumulative prices are designed to work with overflows/underflows,” leading reviewers to assume the arithmetic was intentional, yet the use of unchecked arithmetic is missing, causing an unexpected revert rather than a silent wrap‑around. The problem falls into the class of unchecked arithmetic overflows in financial aggregations. To remediate, the addition and subtraction of cumulative valuations should be wrapped in an unchecked block or the contract should use a larger integer type or a safe‑math library that deliberately handles overflow according to the protocol’s accounting model. Ensuring that the cumulative sum cannot exceed the uint256 range – either by capping inputs, resetting the accumulator periodically, or by using unchecked arithmetic with proper overflow‑aware logic – will prevent the oracle from breaking and keep the protocol’s price calculations reliable.

## Proof of Concept
Cumulative prices are designed to work with overflows/underflows because in the end the difference is important.

In `_updateTwav()` when `_prevCumulativeValuation + (_valuation * _timeElapsed)` overflows the contract will not work anymore.

```solidity
twavObservations[twavObservationsIndex] = TwavObservation(_blockTimestamp, _prevCumulativeValuation + (_valuation * _timeElapsed)); //add the previous observation to make it cumulative @audit overflow breaks the contract
```

Same problem in `_getTwav()`

```solidity
_twav = (_twavObservationCurrent.cumulativeValuation - _twavObservationPrev.cumulativeValuation) / (_twavObservationCurrent.timestamp - _twavObservationPrev.timestamp);@audit same overflow breaks the contract
```

## Recommendation
Add unchecked keyword in every line you add / subtract cumulative prices.

Without a better POC of the issue occurring it’s hard to justify this is High risk. e.g. maybe it could be forced by spamming `updateTWAV`, but it’s not clear if that would require extremely large values or an unrealistic number of transactions.

Related to <https://github.com/code-423n4/2022-06-nibbl-findings/issues/178>, that one includes unchecking the price in the recommendation but the rest of the description focuses on timestamp overflows while this one looks at price overflows.
