# [M] Minting via mintGTToAddress may revert

## Summary
Severity: Medium
Contest weight: 0.5681
Dataset id: 15532
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When minting ERC721 DAO tokens via mintGTToAddress() a check is performed to validate that the user won't end up with more than the max limit:
```solidity
uint256 length = _userAddress.length;
for (uint256 i; i < length;) {
    for (uint256 j; j < _amountArray[i];) {
        if (balanceOf(_userAddress[i]) + _amountArray[i] > erc721DaoDetails.maxTokensPerUser) {
            revert MaxTokensMintedForUser(_userAddress[i]);
        }
        _tokenIdTracker += 1;
        _safeMint(_userAddress[i], _tokenIdTracker);
        _setTokenURI(_tokenIdTracker, _tokenURI[i]);
        unchecked {
            j++;
        }
    }
    unchecked {
        i++;
    }
}
```
So, for example, if the user has 0 NFTs, the max limit is 10, and 10 tokens are minted it should succeed as 0 (balance) + 10 (amount) <= 10 (maxTokensPerUser).
The problem is that this check will be performed after each mint. So, on the next iteration the balance will be one, and 1 (balance) + 10 (amount) <= 10 (maxTokensPerUser) will be false. This will make the transaction revert, and the tokens won't be minted.

## Recommendation
Consider moving the if check outside of the j loop:
```solidity
uint256 length = _userAddress.length;
for (uint256 i; i < length;) {
    if (balanceOf(_userAddress[i]) + _amountArray[i] > erc721DaoDetails.maxTokensPerUser) {
        revert MaxTokensMintedForUser(_userAddress[i]);
    }
    for (uint256 j; j < _amountArray[i];) {
        _tokenIdTracker += 1;
        _safeMint(_userAddress[i], _tokenIdTracker);
        _setTokenURI(_tokenIdTracker, _tokenURI[i]);
        unchecked {
            j++;
        }
    }
    unchecked {
        i++;
    }
}
```
