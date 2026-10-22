# [M] Lumin admin can exploit user allowances to the protocol

## Summary
Severity: Medium
Contest weight: 0.0692
Dataset id: 10103
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The AssetManager contract is used by users to deposit assets into the platform by giving allowance to the contract to execute an ERC20::transferFrom call. The problem is that the contract is upgradeable, meaning the Lumin admin can back-run a user approval to the AssetManager with an upgrade that adds functionality to execute a transferFrom from the user to his address through the contract.

## Recommendation
Put the Lumin Admin role holder address to be behind a Timelock contract so that users can react to admin actions.
