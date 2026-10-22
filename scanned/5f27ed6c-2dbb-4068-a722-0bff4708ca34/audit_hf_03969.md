# [M] [Perennial Self Review] Incorrect price used

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 20332
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of the contract applying an incorrect price when performing value‑dependent operations such as token swaps, collateral valuation, or fee calculation. The root cause is a logic error that selects a stale or wrong price source, misapplies a conversion factor, or fails to update the price after a state change. An attacker can trigger a transaction that relies on the faulty price, for example by initiating a swap or a liquidation, and receive a result that deviates from the expected economic outcome. Because the contract trusts the erroneous price, the user may receive fewer tokens than anticipated, a liquidation may be executed prematurely, or fees may be under‑collected, leading to a loss of funds for users or the protocol. The issue manifests whenever the affected function reads the price variable without proper validation, typically after a price update event or when multiple price feeds exist. All participants that interact with the pricing logic – regular users, liquidity providers, or the protocol itself – are potentially affected. The flaw was discovered during a manual audit where the reviewer noticed that the price variable used in the calculation did not correspond to the most recent feed and that the code path lacked a sanity check. The problem can be subtle because the contract still executes successfully and does not revert, so the incorrect outcome may only be observed as a discrepancy in balances or missing refunds. To remediate, the contract should enforce the use of a verified, up‑to‑date price source, add explicit checks that the price is within an acceptable range, and ensure that any state‑changing operation refreshes the price before use. In broader terms, this is a classic case of a pricing oracle misuse or arithmetic mis‑application that breaks the accounting assumptions of the system, causing funds to disappear or refunds to be calculated incorrectly.

## Recommendation
No recommendation available
