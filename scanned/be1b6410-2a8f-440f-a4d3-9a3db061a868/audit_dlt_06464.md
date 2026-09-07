# [M] Аdditional verification is missing in `isApprovedOrOwner` function

## Summary
Severity: Medium
Chain: Smart contract
Component: Tapioca
Published: 2024-05-29
Source: https://github.com/hats-finance/Tapioca-0xe0b920d38a0900af3bab7ff0ca0af554129f54ad/issues/25
Type: hats-finding

## Details
**Github username:** @Jelev123
**Twitter username:** zhulien_zhelev
**Submission hash (on-chain):** 0xc35a88f5f3afd660e8195fd0a25c5c6b700c9d1f0e57572cac7c0abaab029e88
**Severity:** medium

**Description:**
**Description**\
In [isApprovedOrOwner](https://github.com/hats-finance/Tapioca-0xe0b920d38a0900af3bab7ff0ca0af554129f54ad/blob/ed5d47ef05ddc61c10cd71e7104b44a99c665d55/contracts/options/oTAP.sol#L61) 
function in `oTAP.sol` is missing check for `isERC721Approved(_ownerOf(_tokenId), _spender, address(this), _tokenId);` as done in [this](https://github.com/hats-finance/Tapioca-0xe0b920d38a0900af3bab7ff0ca0af554129f54ad/blob/ed5d47ef05ddc61c10cd71e7104b44a99c665d55/contracts/option-airdrop/aoTAP.sol#L74) function



1. **Proof of Concept (PoC) File**
```solidity
function isApprovedOrOwner(address _spender, uint256 _tokenId) external view returns (bool) {
        return _isApprovedOrOwner(_spender, _tokenId);
    }
```

**Recommendation*

Do the extra check
```solidity
function isApprovedOrOwner(address _spender, uint256 _tokenId) external view returns (bool) {
        return _isApprovedOrOwner(_spender, _tokenId)
            || isERC721Approved(_ownerOf(_tokenId), _spender, address(this), _tokenId);
    }
```
