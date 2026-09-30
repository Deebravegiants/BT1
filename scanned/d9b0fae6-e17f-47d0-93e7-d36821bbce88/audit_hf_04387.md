# [M] Centralization risks with a lot of power vested in the `Reporter` role

## Summary
Severity: Medium
Contest weight: 0.1466
Dataset id: 21615
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
** In the current design, the `Reporter`, a protocol-controlled address, is responsible for executing a number of mission-critical operations. Only `Reporter` operations include starting & finalizing a report, selecting & replacing operators, syncing/activating/withdrawing and depositing validators, verifying & claiming rewards from EigenLayer, etc. Also noteworthy is the fact that the timing and sequence of these operations are crucial for the proper functioning of the Casimir protocol.

** With so many operations controlled by a single address, a significant part of which are initiated off-chain, the protocol is exposed to all the risks associated with centralization. Some of the known risks include:

- Compromised/lost private keys that control the `Reporter` address
- Rogue admin
- Network downtime
- Human/Automation errors associated with the execution of multiple operations

## Recommendation
** While we understand that the protocol in the launch phase wants to retain control over mission-critical parameters, we strongly recommend implementing the following even at the launch phase:

- Continuous monitoring of off-chain processes
- Reporter automation via a multi-sig

In the long term, the protocol should consider a clear path towards decentralization.
