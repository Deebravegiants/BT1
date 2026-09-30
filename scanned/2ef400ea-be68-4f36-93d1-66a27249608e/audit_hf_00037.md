# [M] OCL-2 | Missing Grace Period Check

## Summary
Severity: Medium
Contest weight: 0.0304
Dataset id: 113
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the absence of a freshness validation step in the oracle price retrieval routine. Specifically, the getOraclePrice function does not verify whether the underlying price feed has been updated within an expected grace period before returning a value. The root cause is a missing time‑based check that would compare the timestamp of the latest feed update against the current block timestamp and reject stale data. Because the function can return a price that has not been refreshed for an extended interval, an attacker or any party that can control the timing of feed updates can cause the contract to use an outdated price for calculations such as token swaps, collateral valuations, or liquidation triggers. When a stale price is used, the protocol’s accounting assumptions are violated: users expect that the price reflects the most recent market state, but instead they receive a value that may be significantly lower or higher than the current market. This can lead to incorrect trade execution, unexpected liquidations, or loss of capital, effectively causing funds to disappear from a user’s perspective. The issue manifests whenever the oracle feed fails to update within its normal schedule – for example, if the data source is delayed, compromised, or deliberately left unchanged – and the contract proceeds to query the price without checking the elapsed time. All participants who rely on accurate pricing – traders, lenders, borrowers, and the protocol itself – are impacted. The flaw was discovered during a manual security audit in which the auditor reviewed the oracle integration logic and noted that no grace‑period enforcement was present. The problem can be subtle because the price value may appear reasonable, and there is no explicit error or event indicating staleness, making it difficult to detect through ordinary testing or monitoring. To remediate the issue, the getOraclePrice function should incorporate a check that the difference between the current block timestamp and the timestamp of the last feed update does not exceed a predefined grace period; if it does, the function must revert or fallback to a safe price source. This class of bug is commonly referred to as an "oracle price staleness" or "missing freshness validation" vulnerability, and it violates the fundamental business rule that pricing data must be current to ensure fair and secure protocol operations.

## Recommendation
Implement a grace period check for the getOraclePrice function.
