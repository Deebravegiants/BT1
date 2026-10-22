# [M] Service fees should depend on asset

## Summary
Severity: Medium
Contest weight: 0.0225
Dataset id: 15206
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a service fee that is applied as a constant amount regardless of which asset a user interacts with. The root cause is that the contract stores a single fixed fee value instead of a per‑asset fee structure, ignoring the fact that different tokens have widely varying market prices. When a user submits a transaction using a low‑value asset, the fixed fee represents a much larger proportion of the transaction value than when a high‑value asset is used, creating a price‑based arbitrage window. An attacker can exploit this by repeatedly performing operations with assets whose market price makes the fixed fee disproportionately cheap, effectively extracting value from the protocol or other users. The impact is economic: the protocol may lose revenue, users may receive less service for the same fee, and the overall token economics can become distorted. This condition occurs whenever the contract supports multiple assets with differing USD values while still charging a single static fee. All participants who rely on the service – end‑users, token holders, and the protocol itself – are affected because the fee model does not reflect the true cost of processing each asset. The issue was discovered during a manual audit review of the fee calculation logic, where the auditor noted that the fee does not reference any price feed or asset‑specific mapping. Because the contract still executes successfully and does not revert, the problem can be hard to notice without a detailed economic analysis; the code appears functional, yet the business rule of proportional fees is violated. To remediate, the contract should replace the fixed fee with a mapping that stores a distinct fee for each supported asset, ideally derived from a reliable price oracle or a configurable table, ensuring that the fee scales with the asset’s market value. This change aligns the implementation with the intended business logic that fees reflect the value of the processed asset, eliminating the arbitrage opportunity and restoring economic fairness.

## Recommendation
Set a mapping for service fees.
