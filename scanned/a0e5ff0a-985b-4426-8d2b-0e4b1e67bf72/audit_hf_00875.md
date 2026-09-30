# [M] Contracts of the codebase will

## Summary
Severity: Medium
Contest weight: 0.1148
Dataset id: 2631
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Contracts of the codebase isn't strictly compliant with the ERC-1504. This breaks the readme. As per readme: Is the codebase expected to comply with any EIPs? Can there be/are there any deviations from the specification? Strictly compliant: ERC-1504: Upgradable Smart Contract But the contracts of the codebase uses openzepplin upgradable contracts as base contract which are not compliant with ERC-1504. As per ERC-1504, the upgradable contract should consists of have handler contract, data contract and optionally the upgrader contract. But the contracts of the codebase are not compliant with ERC-1504 because they has no data contract and has data inside the handler contract. Internal pre-conditions External pre-conditions Attack Path Break the readme.

## Recommendation
Make the contracts strictly compliant with ERC-1504.
