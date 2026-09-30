# [M] Centralization Risks

## Summary
Severity: Medium
Contest weight: 0.0350
Dataset id: 17077
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The reported issue is a centralization risk inherent in the contract’s governance and control structures. At its core, the vulnerability stems from an overly concentrated authority model in which a single address, role, or small group possesses the ability to modify critical protocol parameters, upgrade the contract, pause or unpause functionality, and potentially transfer or freeze user assets without broader community oversight. Because the privileged entity can unilaterally execute these high‑impact actions, an attacker who compromises that entity, or a malicious insider, can exploit the design to alter fee structures, redirect withdrawals, or halt service, thereby causing loss of funds, erosion of user trust, and disruption of the protocol’s economic incentives. The impact manifests when a user attempts a normal operation—such as withdrawing a deposit or expecting a promised yield—but the centralized controller intervenes to block the transaction, change the calculation, or reroute the payout, leading to symptoms like empty balances, missing rewards, or complete denial of service. This condition materializes whenever the contract’s privileged functions are invoked, especially in scenarios where a single private key is used for governance, the contract is upgradable via an admin‑only proxy, or emergency stop mechanisms lack a timelock or multi‑signature safeguard. The risk was identified during a systematic audit that examined the ownership model, upgrade pathways, and access control lists, noting that the concentration of power was not mitigated by decentralized voting, quorum requirements, or external audits. Detecting this problem can be difficult because the contract may function correctly under normal conditions, masking the hidden power held by the central authority until an exploit occurs or a key is compromised. To address the issue, the protocol should shift to a more decentralized governance framework—such as multi‑signature wallets, timelocked upgrades, or token‑based voting—ensuring that no single actor can unilaterally alter protocol state or financial flows. By distributing decision‑making authority and introducing transparent, community‑driven checks, the contract can align with its expected trust model and prevent scenarios where funds disappear, refunds are blocked, or the system can be shut down by a single point of failure.

## Recommendation
No recommendation
