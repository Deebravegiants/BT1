# [M] Hidden governance

## Summary
Severity: Medium
Contest weight: 0.1240
Dataset id: 1615
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a fragmented governance architecture in which a single token contract simultaneously employs two independent authority models: a custom "VanillaGovernable" layer and the OpenZeppelin AccessControl‑based role system inherited from ERC20PresetMinterPauserUpgradeable. This dual‑governance arrangement creates a hidden control path because privileged functions such as mint, pause, and other admin actions are governed by the role‑based layer, while the public governance interface exposed by VanillaGovernable suggests a different set of decision makers. The root cause is the accidental (or deliberate) combination of two governance contracts without a clear mapping of which functions each authority controls, leading to ambiguous ownership and the potential for an actor with role‑based privileges to perform critical state changes without being reflected in the visible governance UI. An attacker—or even a trusted administrator—could exploit this by acquiring or being granted the appropriate AccessControl role (e.g., MINTER_ROLE or PAUSER_ROLE) and then minting new VUSD tokens, pausing transfers, or otherwise manipulating the contract while the VanillaGovernable governance records show no corresponding proposal or vote. The impact is a breach of the protocol’s accounting assumptions: users may see their balances increase unexpectedly, experience unexplained pauses, or lose trust because the governance process they observe does not actually safeguard the most sensitive operations. The issue manifests whenever the contract is deployed with both inheritance lines active, which is the case for the VUSD contract examined in the audit. All participants—token holders, liquidity providers, and downstream protocols that rely on VUSD—are affected because they cannot reliably verify who controls minting and pausing. The problem was discovered during a manual source‑code review that highlighted the inheritance hierarchy and compared the function modifiers used across the contract. It can be hard to notice because both governance modules are technically functional, and automatic tools may not flag the semantic inconsistency between them. To remediate, the contract should be refactored to a single, unified governance model—either by consolidating everything under vanilla governance with explicit admin functions, or by adopting a role‑based AccessControl scheme such as OZ's AccessControlledAndUpgradeable—so that every privileged action is governed by the same transparent decision‑making process. This eliminates hidden authority, aligns UI expectations (users expect that governance proposals control minting and pausing) with reality, and restores confidence that the protocol’s accounting rules are enforced by an auditable and single source of truth.

## Proof of Concept
The [VUSD contract](https://github.com/code-423n4/2022-02-hubble/blob/8c157f519bc32e552f8cc832ecc75dc381faa91e/contracts/VUSD.sol#L11) uses `VanillaGovernable` but inherits from `ERC20PresetMinterPauserUpgradeable` and this contract uses roles to use some administrative methods like `pause` or `mint`.

This two-governance model does not seem necessary and can hide or raise suspicion about a rogue pool, thus damaging the user’s trust.

## Recommendation
Unify governance in only one, VanillaGovernable or role based.

Yes, a good suggestion to keep governance more tightly coupled. OZ has AccessControlledAndUpgradeable which is really nice. Various roles for varying level of admin functionality. Allows tighter controls on more controversial items and easier control on less controversial items.
