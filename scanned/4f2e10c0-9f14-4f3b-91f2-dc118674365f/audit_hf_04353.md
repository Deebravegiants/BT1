# [M] M-03 | Blast Yields Are Not Conﬁgured For YesArena

## Summary
Severity: Medium
Contest weight: 0.0357
Dataset id: 21512
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The YesArena smart contract lacks any configuration or mechanism to handle gas yields that may be generated during gameplay. This omission originates from the contract not integrating the Blast gas‑rebate system, which is designed to accumulate and later allow the contract to claim refunds for gas spent on certain operations. Because the contract does not track or expose functions for claiming these yields, any gas rebates that would otherwise be credited remain unclaimed and effectively locked inside the contract. An attacker or even a regular user cannot exploit this directly to steal funds, but the economic impact is that the protocol and its participants incur higher net gas costs than necessary, reducing overall efficiency and potentially eroding user trust. The issue manifests whenever the YesArena game executes transactions that trigger gas‑yield generation – for example, during match creation, move submissions, or settlement – and the contract does not provide a way to retrieve the accrued rebate. Users may notice that their transaction receipts show higher gas consumption without the expected reduction in cost, or that the contract’s balance does not reflect any reclaimed gas. The vulnerability was identified during a systematic audit of the contract’s financial flows, where the absence of Blast‑related configuration stood out as a logical gap. It can be difficult to spot because the contract still functions correctly from a functional standpoint; the missing yields are a silent loss that does not cause outright failures. To remediate, the contract should be extended with appropriate state variables and public functions that record gas‑yield accruals and enable the owner or designated role to claim the accumulated gas refunds, aligning the implementation with the intended Blast yield model and restoring the expected economic behavior of the protocol.

## Recommendation
Consider implementing appropriate configurations and functions to claim the gas yields that would accrue for the YesArena contract.
