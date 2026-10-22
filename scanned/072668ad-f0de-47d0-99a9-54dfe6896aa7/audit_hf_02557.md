# [M] Susceptibility to Reorg Attacks

## Summary
Severity: Medium
Contest weight: 0.0627
Dataset id: 13704
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Reorgs attacks occur most times on L2 chains, and the Portal and VirtualLP contracts use the non-deterministic create method for deploying the bToken and portalEnergyToken. Due to the use of create to deploy these contracts, in the case of a reorg event, the addresses will change and users who have used the previous contract’s tokens or tokenIDs will lose them.

## Recommendation
Consider using create2 with a non-deterministic salt + the msg.sender instead.
