# [H] Governance veto can be bypassed

## Summary
Severity: High
Contest weight: 0.1599
Dataset id: 1214
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a governance veto bypass that allows a malicious proposal to become immune to the council's veto power. The root cause lies in the veto logic of the GovernorAlpha contract, which checks that none of the actions in a proposal target the governance contract itself. Because the check only validates the presence of a self‑referencing action at the proposal level, an attacker can embed a single harmless or arbitrary call whose destination is the GovernorAlpha contract. This single action triggers the veto condition to treat the entire proposal as non‑vetoable, effectively disabling the veto mechanism for that proposal. Exploitation is straightforward: an attacker crafts a proposal that includes the desired malicious actions (such as altering the council composition or upgrading contracts) and appends an additional action that calls the governance contract with a no‑op payload. When the proposal reaches the execution stage, the veto function sees the self‑referencing call and skips the veto check, allowing the proposal to be executed even though the council expected to be able to block it. The impact is severe: the protocol can undergo unauthorized governance changes, resulting in loss of decentralized control, potential theft of funds, or alteration of critical parameters without community oversight. The condition occurs whenever a proposal contains at least one action whose target address equals the GovernorAlpha contract address, regardless of the other actions' content. All participants who rely on the veto—council members, token holders, and users—are affected because they lose the safety valve that was presumed to prevent hostile governance moves. The issue was discovered during a Code4rena audit, where the reviewers noticed that the veto function only examined the list of actions for a simple address match and did not account for the scenario where a single self‑targeted call disables veto for the whole proposal. This flaw can be hard to spot because the code appears to safeguard against proposals that directly manipulate the governance contract, yet the presence of a benign self‑call unintentionally creates an exemption. To remediate, the veto mechanism should be redesigned to evaluate each action individually and enforce that any proposal containing a governance‑contract call remains vetoable, possibly by introducing a whitelist of permissible functions or by requiring that veto checks are based on the nature of the invoked function rather than merely the destination address. In user‑facing terms, a proposal that should have been blocked may execute, leading to unexpected changes such as council members disappearing, contract upgrades occurring without consent, or balances being affected, while the UI still shows that the veto button was unavailable. This violation breaks the fundamental business logic that governance proposals can be reviewed and stopped by the council, undermining the protocol's trust model.

## Proof of Concept
For any attacker who want to launch a governance attack using a malicious proposal, they simply need to add an action that point to governance that does nothing (or anything).

## Recommendation
Some other design can be proposal are vetoable whenever the differential is less than x%, even if it involves governance change, s.t. council can veto most malicious proposal while it is still possible to change council given high enough vote differential.

Duplicate of #61

Not a duplicate
