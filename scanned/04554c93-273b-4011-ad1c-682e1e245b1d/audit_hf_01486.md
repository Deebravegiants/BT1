# [H] H-4 FantiumNFTV1.owners shadows ERC721Upgradeable.owners

## Summary
Severity: High
Contest weight: 0.5303
Dataset id: 7904
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
FantiumNFTV1 mapping(uint256 => address) internal _owners shadows ERC721Upgradeable mapping(uint256 => address) private _owners. Thus, the exists() (FantiumNFTV1.sol#L245-L248) function will not work correctly:
```solidity
function exists(uint256 _tokenId) public view returns (bool) {
    return owners[tokenId] != address(0);
}
```

## Recommendation
1. Remove the FantiumNFTV1 mapping(uint256 => address) internal _owners line. 2. Use the ERC721Upgradeable.ownerOf() method. 2.3 Medium
