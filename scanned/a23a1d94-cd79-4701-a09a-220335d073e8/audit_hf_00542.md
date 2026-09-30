# [H] H-02 | Collector Allocations Errantly Validated

## Summary
Severity: High
Contest weight: 0.1575
Dataset id: 2000
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the AnimeClaimer contract when the claimer is the collector for a collector vest then there is no further validation performed on the vest and the vested amount is granted to the collector address on the L2. However the owner of the collector address on the L2 may be different then the owner of the collector address on the L1. For example, a smart contract wallet/multisig could have been transferred from Alice to Bob on the L1, but Alice may have kept ownership of a smart contract wallet/multisig deployed at the same address on the L2.

## Recommendation
Ensure that all collector addresses which are awarded are EOAs on both chains. If this is not the case then a more adept verification process is necessary.
