# [M] Lack of isSmartContract check

## Summary
Severity: Medium
Contest weight: 0.5771
Dataset id: 9395
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The initForSmartAccount function in the KlasterEcdsaModule contract is responsible for initializing the module for a Smart Account and setting the EOA owner. However, it doesn't include a check to ensure that the provided eoaOwner address is not a smart contract.
```solidity
function initForSmartAccount(address eoaOwner) external returns (address) {
    if (_smartAccountOwners[msg.sender] != address(0)) {
        revert AlreadyInitedForSmartAccount(msg.sender);
    }
    if (eoaOwner == address(0)) revert ZeroAddressNotAllowedAsOwner();
    _smartAccountOwners[msg.sender] = eoaOwner;
    return address(this);
}
```
While the contract includes a _isSmartContract function to check if an address is a smart contract, it is not utilized in the initForSmartAccount function. This means that it is possible to set a smart contract as the owner of a Smart Account during initialization. Although the provided information suggests that this doesn't compromise security due to the requirement of valid EOA signatures for operations, it is still worth considering adding the isSmartContract check for consistency and enforcing the intended behavior of only allowing EOA owners.

## Recommendation
To improve the clarity and enforceability of the intended behavior, it is recommended to add the isSmartContract check in the initForSmartAccount function. This ensures that only EOA addresses can be set as owners during the initialization of a Smart Account. Here's the updated code with the isSmartContract check:
```solidity
function initForSmartAccount(address eoaOwner) external returns (address) {
    if (_smartAccountOwners[msg.sender] != address(0)) {
        revert AlreadyInitedForSmartAccount(msg.sender);
    }
    if (eoaOwner == address(0)) revert ZeroAddressNotAllowedAsOwner();
    if (_isSmartContract(eoaOwner)) revert NotEOA(eoaOwner);
    _smartAccountOwners[msg.sender] = eoaOwner;
    return address(this);
}
```
By adding the if (_isSmartContract(eoaOwner)) revert NotEOA(eoaOwner); line, the function will revert if the provided eoaOwner address is a smart contract, ensuring that only EOA addresses can be set as owners.
