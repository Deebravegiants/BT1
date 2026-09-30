# [H] H-07 | All Gas Yields Earned On Blast Are Lost

## Summary
Severity: High
Contest weight: 0.1317
Dataset id: 21502
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
This protocol will be deployed on Blast, which provides a feature to claim gas fees consumed by smart contracts. Contracts can claim 50% to 100% of gas fees depending on the claim rate. The default gas mode for contracts on Blast is Void, and all consumed gas is sent to the sequencer. For these gas fees to be claimed, smart contracts must be configured by interacting with the BLAST contract at 0x4300000000000000000000000000000000000002 address.

## Recommendation
Configure smart contracts to set gas mode claimable, and use this additional income to increase blv.
