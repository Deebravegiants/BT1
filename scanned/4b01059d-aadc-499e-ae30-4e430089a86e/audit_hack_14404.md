# [M] MeritNFT contract does not comply with ERC721 and it breaks composability

## Summary
Severity: Medium
Reporter: sorrynotsorry
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L84-L92
Type: audit-issue

## Details
# MeritNFT contract does not comply with ERC721 and it breaks composability

## Summary
MeritNFT contract does not comply with ERC721 and it breaks composability
## Vulnerability Detail
MeritNFT implements supportsInterface as below: 
```solidity
function supportsInterface(bytes4 interfaceId)
    public
    view
    virtual
    override(AccessControlEnumerable, ERC721Enumerable)
    returns (bool)
{
    return super.supportsInterface(interfaceId);
}
```
This call will return;

```solidity
function supportsInterface(bytes4 interfaceId) public view virtual override returns (bool) {
    return interfaceId == type(IAccessControlEnumerable).interfaceId || super.supportsInterface(interfaceId);
}
```

The issue is that it will only support the ERC721 extensions, and does not comply with ERC721 itself. From [EIP721](https://eips.ethereum.org/EIPS/eip-721):
"Every ERC-721 compliant contract must implement the ERC721 and ERC165 interfaces"


It should explicitly check for;
```solidity
interfaceId == type(IERC721Enumerable).interfaceId
```
## Impact
The NFT will fail to get in interaction with the other contracts
## Code Snippet

```solidity
function supportsInterface(bytes4 interfaceId)
    public
    view
    virtual
    override(AccessControlEnumerable, ERC721Enumerable)
    returns (bool)
{
    return super.supportsInterface(interfaceId);
}
```
[Link](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L84-L92)
## Tool used

Manual Review

## Recommendation
Check for 
```solidity
interfaceId == type(IERC721Enumerable).interfaceId
```
