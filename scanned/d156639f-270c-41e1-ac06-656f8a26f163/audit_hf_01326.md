# [H] marketOrder() with expendOutput reverts with SlippageError with max tolerance

## Summary
Severity: High
Contest weight: 0.0257
Dataset id: 6580
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the marketOrder function of the Clober decentralized exchange where the slippage validation logic uses the expendOutput value incorrectly. When a user submits a market order, the contract calculates the amount that will be spent (expendOutput) and compares it against a slippage tolerance parameter supplied by the caller. The implementation mistakenly applies the tolerance check to the wrong side of the inequality, causing the transaction to revert with a SlippageError even when the caller has set the maximum possible tolerance (for example 100%). This logical error means that the order cannot be executed under any circumstances, effectively creating a denial‑of‑service condition for market orders. The bug was discovered during a security audit performed by Spearbit, who noted that the function reverts consistently despite the tolerance being set to its maximum. Because the failure occurs deep inside the order execution path, it may not be obvious from the user interface; users simply see their transaction fail with a generic slippage error and may assume a network issue or a malicious contract. The impact is that traders are unable to place market orders, leading to lost trading opportunities, potential fee loss for liquidity providers, and a perception that the protocol is unreliable. Funds are not actually transferred or stolen; the transaction is reverted, but users still incur gas costs. The issue affects any participant who attempts to trade on the platform, including regular users, market makers, and protocol operators. It is hard to notice because the error only surfaces when the slippage tolerance is explicitly set to its maximum, a scenario that many test suites do not cover. The proper fix is to correct the slippage comparison so that the contract validates the actual output against the tolerance in the intended direction, ensuring that a market order only reverts when the real slippage exceeds the user‑specified limit. Conceptually, this is a logical validation bug in the slippage checking routine, a class of errors where business rules are implemented incorrectly, leading to unintended reverts and broken accounting assumptions.

## Recommendation
Clober: Fixed in commit fdf90626.
