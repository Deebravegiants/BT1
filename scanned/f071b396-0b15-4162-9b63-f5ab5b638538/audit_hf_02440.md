# [M] Revisited Assumption on Trusted Governance

## Summary
Severity: Medium
Contest weight: 0.1791
Dataset id: 13098
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Stone protocol, the governance account plays a critical role in governing and regulating the system-wide operations (e.g., vault/strategy addition, reward adjustment, and parameter setting). It also has the privilege to control or govern the flow of assets for investment or full withdrawal among the three components, i.e., vault, controller, and strategy.

With great privilege comes great responsibility. Our analysis shows that the governance account is indeed privileged. In the following, we examine the current privilege management graph in the Stone protocol (Figure 3.1).

Public
Figure 3.1: The Privilege Management Chain in Stone

We emphasize that the privilege assignment among vault, controller, and strategy is properly administrated. However, it is worrisome that governance is not governed by a DAO-like structure. The discussion with the team has confirmed that the governance will be managed by a multi-sig account.

We point out that a compromised governance account would allow the attacker to add a malicious controller to steal all funds whenever the earn() call is made. It could also allow for the dynamic addition of a new malicious strategy, which directly undermines the assumption of the Stone protocol.

## Recommendation
Promptly transfer the governance privilege to the intended DAO-like governance contract. And activate the normal on-chain community-based governance life-cycle and ensure the intended trustless nature and high-quality distributed governance.
