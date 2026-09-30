# [M] Attacker can frontrun deployVault to deploy at the same address

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-pooltogether
Published: 2023-07-14
Source: https://github.com/code-423n4/2023-07-pooltogether-findings/issues/416
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-vault/blob/b1deb5d494c25f885c34c83f014c8a855c5e2749/src/VaultFactory.sol#L67-L78


# Vulnerability details

## Impact
Vaults are created from the factory via CREATE1, an attacker can frontrun deployVault to deploy at the same address but with different config. If the deployed chain reorg, a different vault might also be deployed at the same address.

## Proof of Concept
https://github.com/GenerationSoftware/pt-v5-vault/blob/b1deb5d494c25f885c34c83f014c8a855c5e2749/src/VaultFactory.sol#L67-L78
1. Bob setup a bot to monitor the mempool when PT deploy a new vault
2. Bob's bot saw a deployment by PT at 0x1234, fire a tx to deposit immediately
3. Alice frontrun PT's deployment by deploying a malicious vault at 0x1234
4. Bob's transaction ended up deposited into Alice's malicious vault

## Recommended Mitigation Steps
Use CREATE2 and the vault config as salt.


## Assessed type

MEV
