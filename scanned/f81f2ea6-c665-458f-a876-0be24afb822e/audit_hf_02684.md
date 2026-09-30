# [M] Duplicate PoolIds Can Cause Loss Of Funds For Users

## Summary
Severity: Medium
Contest weight: 0.2086
Dataset id: 14541
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Withdrawal vaults handle the distribution of rewards to users, node operators and protocol fee recipients. Due to the use of CREATE2 opcode and contract architectural decisions, accidental or malicious administration can generate the same withdrawal address over two pool registries with identical poolIds.
VaultFactory.deployWithdrawVault() and VaultFactory.computeWithdrawVaultAddress() use the OpenZeppelin Clones Upgradeable contracts to manage the creation of new withdrawal vaults. In turn these use CREATE2 with a salted value that relies on _poolId, _operatorId, _validatorCount. These values are entirely determined by the PoolRegistry contracts, which means that salt hash collisions can occur, resulting in the same withdrawal address being calculated.
If two users share the same withdrawal address across two different pool registry contracts, it is possible for the earlier user to steal funds of the latter user.
Currently PermissionlessNodeRegistry and PermissionedNodeRegistry use the VaultFactory.deployWithdrawVault() which will revert if the same address is calculated twice (since CREATE2 reverts if an address has non-zero nonce, or has extcodesize>0). However, PermissionlessPool.preDepositOnBeaconChain() uses VaultFactory.computeWithdrawVaultAddress which will not be able to differentiate between whether vault is being calculated that matches a different pool with the same poolId.

## Recommendation
Instead of poolId, use registry address (msg.sender) and pass this information to the pool contracts as well, this will protect against accidental poolId collisions from potentially causing loss of funds. It will not protect against malicious action, but the current access control (ie. NODE_REGISTRY_CONTRACT) here will restrict the attack surface to administrative accounts only. An alternative is moving deployWithdrawVault (ie CREATE2) logic to the pool registry contracts (though this would defeat the purpose of the VaultFactory).
