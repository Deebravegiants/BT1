# [M] KeyLocker.supportsInterface() returns false for type(IERC1155Receiver).interfaceId

## Summary
Severity: Medium
Contest weight: 0.6596
Dataset id: 10001
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
KeyLocker.supportsInterface() incorrectly returns false when called with the interface ID of IERC1155Receiver, which violates the ERC-1155 specification and could break composability with other contracts.

supportsInterface() in KeyLocker.sol checks the following interface IDs:
```solidity
return interfaceId == type(IKeyLocker).interfaceId ||
       interfaceId == type(IERC165).interfaceId ||
       interfaceId == type(ERC1155Holder).interfaceId;
```
However, the function incorrectly checks for type(ERC1155Holder).interfaceId instead of type(IERC1155Receiver).interfaceId.

## Recommendation
Instead of including the interface IDs of all inherited contracts, consider calling super.supportsInterface():
```solidity
return interfaceId == type(IKeyLocker).interfaceId ||
       interfaceId == type(IERC165).interfaceId ||
       interfaceId == type(ERC1155Holder).interfaceId;
+ super.supportsInterface(interfaceId);
```
This will also call the supportsInterface() function of ERC1155Holder. For consistency, consider modifying Locksmith.supportsInterface() as well:
```solidity
return interfaceId == type(IERC1155).interfaceId ||
       interfaceId == type(IERC1155MetadataURI).interfaceId ||
       interfaceId == type(ILocksmith).interfaceId ||
       interfaceId == type(IERC165).interfaceId;
+ super.supportsInterface(interfaceId);
```
