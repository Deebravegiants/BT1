# [H] Incorrect NFT Removal Logic in SmartChefNFT

## Summary
Severity: High
Contest weight: 0.6045
Dataset id: 11850
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The DackieSwap protocol has a built-in SmartChefNFT contract that allows the liquidity provider to farm their Pancake V3 NFT Positions to earn rewards. In the process of examining the NFT addition/removal logic, we notice a potential issue that needs to be fixed. To elaborate, we show below the implementation of the related removeTokenId() routine. This routine is used to remove a specific tokenId from a user. However, it comes to our attention that this routine may be abused to withdraw a tokenId that does not belong to the withdrawing user even though it may have the cost of losing one of his NFT positions. In other words, the user may create a NFT position with tiny liquidity and steal another user's NFT position with larger liquidity.
```solidity
function removeTokenId(UserInfo storage _user, uint256 _tokenId) internal {
    uint256[] storage tokenIds = _user.tokenIds;
    uint256 indexToBeDeleted;
    for (uint256 i = 0; i < tokenIds.length; i++) {
        if (tokenIds[i] == _tokenId) {
            indexToBeDeleted = i;
            break;
        }
    }
    if (indexToBeDeleted < tokenIds.length - 1) {
        tokenIds[indexToBeDeleted] = tokenIds[tokenIds.length - 1];
    }
    tokenIds.pop();
    // Withdraw NFT from contract
    stakedToken.transferFrom(address(this), msg.sender, _tokenId);
    uint256 rarity = getRarity(_tokenId);
    _user.amount -= rarity * BASE_FACTOR;
    totalStake -= rarity * BASE_FACTOR;
}
```

## Recommendation
Revisit the above removeTokenId() routine to ensure the requested tokenId belongs to the withdrawing user.
