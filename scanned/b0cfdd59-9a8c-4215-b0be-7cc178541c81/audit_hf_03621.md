# [M] Using one controller for two addresses could

## Summary
Severity: Medium
Contest weight: 0.2233
Dataset id: 19682
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The DNGMXVaultController is intended to be used as a controller for two separate contracts when interacting with Rage Trade. While individual contracts check for signature collisions, there is no protection in this Controller. If the contracts end up with functions with colliding signatures, this may enable users to call illegal functions and get around the protocol safeguards.
While most of Sentiment's Controllers correspond to one contract, the DNGMXVaultController is one controller that will support two separate contracts: DepositPeriphery and WithdrawPeriphery.
While signature collisions are unlikely, they do happen. For this reason, the Solidity compiler stops code from compiling in the case of a collision. This ensures that there will not be issues in any EVM bytecode. Because Sentiment controllers approve function calls based on signatures, they can be sure that, for any given contract, they will only be approving the function they are intending.
However, once multiple contracts are managed by one controller, there are no compiler checks across these contracts for colliding signatures. The result is that there is the potential for a function signature on one contract that is approved, due to a matching signature on the other contract.
There is the potential for users to get access to non-permitted functions if there is a signature collision.
This is a security risk in this specific case, but is also a more global suggestion for Sentiment. While two contracts on one Controller one time is unlikely to cause a problem, the practice of loading multiple contracts onto on Controller should be avoided, as the risks will increase as this is performed.

## Recommendation
Split DNGMXVaultController into two files, one for each of the two contracts that will be interacted with.
Going forward, continue to uphold the practice of always having one Controller per contract, unless the two contracts are identical and non-upgradeable.
