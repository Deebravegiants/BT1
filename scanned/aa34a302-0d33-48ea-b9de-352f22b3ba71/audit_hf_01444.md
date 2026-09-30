# [M] M-2 Reserve oracle

## Summary
Severity: Medium
Contest weight: 0.0294
Dataset id: 7519
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from the protocol’s reliance on a single Chainlink price oracle to provide a continuous price history used by the settle function. When the Chainlink feed experiences instability, such as network congestion, node downtime, or data transmission errors, gaps can appear in the recorded price series. The contract assumes that every price slot contains a valid, non‑zero value and does not include logic to handle missing entries. Consequently, when the settle function attempts to read a price that is absent or zero, the internal arithmetic or validation checks trigger a revert, aborting the transaction. This situation can be triggered unintentionally by natural oracle outages or deliberately by an attacker who forces the feed into a stale state, for example by flooding the network or manipulating the underlying data source. The immediate impact is that settlement operations fail, preventing users from completing trades, claiming rewards, or withdrawing funds, effectively locking assets in the contract until the oracle resumes normal operation. The issue manifests only during periods when the price feed is incomplete; under normal conditions the contract behaves as expected, making the problem hard to detect during routine testing. The affected parties include any user attempting to settle a position, liquidity providers whose capital remains idle, and the protocol itself, which may suffer reputational damage and loss of confidence. The flaw was identified during a security audit performed by MixBytes, which noted that the contract lacks a fallback or reserve price source to cover oracle gaps. Because the revert occurs deep inside business‑logic code, the failure appears as a generic transaction error rather than a clear indication of an oracle problem, complicating debugging. To remediate the issue, the contract should incorporate a reserve price mechanism—such as a secondary oracle, time‑weighted average price, or on‑chain fallback source—and add explicit checks for missing data, allowing the settle function to either use the reserve price or gracefully abort with a user‑friendly error message. This class of bug falls under oracle availability and data‑integrity failures, where insufficient handling of missing external data leads to unexpected contract reverts and potential fund immobilisation.

## Recommendation
We recommend adding some reserve price source for the Oracle contract.
