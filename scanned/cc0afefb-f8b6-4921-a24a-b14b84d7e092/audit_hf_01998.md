# [M] M-2 Ether stuck in the FeeDistributor

## Summary
Severity: Medium
Contest weight: 0.0476
Dataset id: 11241
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a distribution lock in the fee distributor contract. The contract attempts to send Ether to a list of fee receivers in a single loop using a direct call. If any receiver contract rejects the transfer – for example because its fallback function reverts or consumes more gas than the call provides – the whole transaction reverts and the distribution stops. Because the contract does not handle the failure, the Ether that was meant to be split among all receivers remains locked in the distributor's balance. This situation can be triggered whenever the fee distribution function is executed and at least one of the configured receivers is unable to accept Ether. An attacker can deliberately deploy a malicious receiver that always reverts, or a legitimate receiver may be upgraded to a version with a non‑payable fallback, causing the same effect. The impact is that the protocol’s fee pool becomes inaccessible; users and stakers who rely on those fees see no payouts, and the locked Ether is effectively frozen until a new distributor instance is deployed and the funds are manually migrated. The issue was discovered during a manual audit of the FeeDistributor.sol source, where the code at line 231 was identified as performing an unconditional Ether transfer without error handling. The bug is subtle because normal operation works when all receivers are well‑behaved, so the problem only appears after a faulty receiver is added, and there is no explicit error message indicating that the distribution failed. The proper mitigation is to redesign the distribution mechanism: either use a pull‑payment model where each receiver withdraws its share, or wrap each transfer in a try/catch (or low‑level call with a gas stipend) and record failed payouts for later recovery, and provide a migration function that can move any stuck Ether to a fresh distributor contract. This change restores the accounting guarantees of the fee system and prevents Ether from disappearing from the contract balance.

## Recommendation
We recommend implementing the functionality to migrate from a stuck FeeDistributor instance to a new one. 2.4 Low
