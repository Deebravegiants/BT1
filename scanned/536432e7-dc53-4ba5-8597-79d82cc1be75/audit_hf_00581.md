# [M] M-01 | deployVault Calls Can Be Front-run

## Summary
Severity: Medium
Contest weight: 0.1644
Dataset id: 2043
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ExitVaultEntryPoint.deployVault function is designed to deploy a new vault contract using the CREATE2 opcode, mint an ERC721 token representing ownership of the vault and initialize the newly deployed vault with specific parameters. However, the function accepts a _counter parameter provided by the caller, which must match the current proxiesCounter stored in the contract. When a user attempts to deploy a vault by calling deployVault with a specific _counter, an attacker or even a legitimate user could submit their own deployVault transaction with the same _counter before the original one is mined. If this transaction is processed first, it increments the proxiesCounter and successfully deploys a vault. Consequently, when the original user's transaction is executed, the _counter no longer matches the updated proxiesCounter, causing the transaction to revert with an InvalidCounter error. This results in wasted approvals, as users must perform multiple approvals before calling deployVault.

## Recommendation
Remove the proxiesCounter == counter restriction and instead let the user provide any _counter. Instead of then storing the _counter in the mapping(uint256 id => address) public vaults; store the salt: keccak256(abi.encodePacked(_counter, msg.sender)) This will require an update in the vaults mapping as: mapping(uint256 id => bytes32) public vaults Finally, in order to compute the tokenId that must be minted to the owner, convert the bytes32 of the salt to an uint256.
