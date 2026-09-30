# [M] OCL-2 | Median Price Validation

## Summary
Severity: Medium
Contest weight: 0.0395
Dataset id: 17885
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a missing validation check that allows the median maximum price to be set lower than or equal to the median minimum price. This logical error originates from the contract’s price‑range handling code, which accepts two oracle‑derived values – medianMinPrice and medianMaxPrice – without enforcing the fundamental invariant that the maximum must be greater than the minimum. When the invariant is violated, downstream calculations that depend on a proper price interval, such as the pool value, profit‑and‑loss‑to‑pool factor, and other accounting metrics, produce incorrect results. An attacker or a faulty data source can supply a price update where medianMaxPrice ≤ medianMinPrice, causing the contract to compute negative or zero pool values, mis‑price synthetic positions, and potentially allocate insufficient or excessive payouts. From a user’s perspective this may appear as a missing refund, a balance that unexpectedly drops to zero, or a payout that is far lower than expected. The issue is triggered whenever the oracle update routine writes the two price bounds without a guard clause, which can happen during volatile market conditions, data feed glitches, or deliberate manipulation. All participants who rely on the contract’s pricing – liquidity providers, traders, and the protocol itself – are affected because the accounting assumptions that the pool is fully collateralised and that payouts are correctly derived from market prices are broken. The flaw was discovered during a manual audit review that identified the absence of a require statement enforcing medianMaxPrice > medianMinPrice. It is subtle because the contract may still operate with seemingly reasonable numbers, and the error only manifests when the price bounds cross, a scenario that may be rare in normal operation. To remediate the issue, the contract should include an explicit validation step (e.g., require(medianMaxPrice > medianMinPrice)) before any calculations that use these values, ensuring that the price interval is always well‑formed and that downstream financial formulas remain sound.

## Recommendation
Implement the validation that medianMaxPrice is greater than the medianMinPrice.
