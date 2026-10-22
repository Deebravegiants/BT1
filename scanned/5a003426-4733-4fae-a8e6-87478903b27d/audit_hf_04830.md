# [M] Edition.supportsInterface is not EIP1155 compatible

## Summary
Severity: Medium
Contest weight: 0.6682
Dataset id: 22715
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to the ERC-1155 specification, the smart contracts that are implementing it MUST have a supportsInterface(bytes4) function that returns true for values 0xd9b67a26 and 0x0e89341c. The current implementation of Edition.sol will return false for both these values.
The contract inherits from ERC1155 and ERC2981.
```solidity
contract Edition is IEdition, ERC1155, ERC2981, Initializable, OwnableRoles
```
The supportsInterface() function of Edition returns the result of executing super.supportsInterface()
```solidity
function supportsInterface(bytes4 interfaceId)
    public
    view
    override(IEdition, ERC1155, ERC2981)
    returns (bool)
{
    return super.supportsInterface(interfaceId);
}
```
Since both ERC1155 and ERC2981 implement that function and ERC2981 is the more derived contract of the two, Edition.supportsInterface() will end up executing only ERC2981.supportsInterface().
Medium. The contract is to be a strict implementation of ERC1155, but it does not implement the mandatory ERC1155.supportsInterface() function.

## Recommendation
Instead of relying on super, return the union of ERC1155.supportsInterface(interfaceId) and ERC2981.supportsInterface(interfaceId).
```solidity
function supportsInterface(bytes4 interfaceId)
    public
    view
    override(IEdition, ERC1155, ERC2981)
    returns (bool)
{
    return ERC1155.supportsInterface(interfaceId) || ERC2981.supportsInterface(interfaceId);
}
```
