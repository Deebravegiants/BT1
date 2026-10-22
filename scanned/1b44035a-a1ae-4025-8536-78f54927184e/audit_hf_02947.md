# [M] M-10 OPERATORFILTERREGISTRY can be missing in a new network

## Summary
Severity: Medium
Contest weight: 0.0438
Dataset id: 16354
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from the VibeERC721 contract’s reliance on the OPERATORFILTERREGISTRY contract through the onlyAllowedOperatorApproval and onlyAllowedOperator modifiers. These modifiers are designed to query a registry that lists which operators are permitted to manage tokens on behalf of owners. The contract assumes that the registry is already deployed on the target blockchain, but it does not verify that the registry address points to a deployed contract. When the VibeERC721 contract is deployed on a new network where the OPERATORFILTERREGISTRY has not been deployed, the calls made by the modifiers resolve to a non‑existent contract. As a result, the registry checks either silently fail or revert, effectively disabling the operator filtering logic. This allows any address to be approved as an operator, bypassing the intended restriction. An attacker can exploit this by deploying the token contract on such a network, then approving a malicious operator who can subsequently transfer or burn the token holder’s NFTs without permission. The impact is that token holders may lose control over their assets, leading to unauthorized transfers, potential loss of NFTs, and erosion of trust in the protocol. The issue manifests only when the contract is instantiated on a blockchain that lacks the OPERATORFILTERREGISTRY deployment; on established networks where the registry exists, the problem is not observable, making it easy to miss during standard testing. The audit team discovered the flaw by reviewing the modifier implementations and noting the missing existence check. From a user’s perspective, a token holder might see that they can approve any operator and that the contract does not block suspicious approvals, contrary to the expectation that only vetted operators are allowed. To remediate, the contract should include an explicit check that the OPERATORFILTERREGISTRY address contains code (e.g., using extcodesize) before invoking its functions, and either revert with a clear error or disable the operator‑filtering feature when the registry is absent. This change ensures that the business logic—restricting token management to approved operators—remains enforced across all networks, preventing accidental or malicious bypass of the operator filter.

## Recommendation
We recommend adding a check that OPERATORFILTERREGISTRY is deployed on the network that will be used for the protocol deployment.
