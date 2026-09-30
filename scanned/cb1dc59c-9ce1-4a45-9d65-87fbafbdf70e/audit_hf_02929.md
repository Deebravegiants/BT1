# [H] spendXP fails if the last NFT lacks balance

## Summary
Severity: High
Contest weight: 0.5924
Dataset id: 16275
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When spending XP in spendXP an equal amount amountPerNFT is subtracted from each NFTs XP:
```solidity
uint256 spent = 0;
uint256 amountPerNFT = amount / stakedNFTs[_address].length;
for (uint256 i = 0; i < stakedNFTs[_address].length; i++) {
    if (stakedNFTs[_address][i].balance >= amountPerNFT) {
        stakedNFTs[_address][i].balance -= amountPerNFT;
        spent += amountPerNFT;
    } else {
        stakedNFTs[_address][i].balance = 0;
        spent += stakedNFTs[_address][i].balance;
    }
}
stakedNFTs[_address][stakedNFTs[_address].length - 1].balance -= (amount - spent);
```
Varonve.md If the NFT doesn't have that much XP all of its XP is removed (see H-02 for another issue with this). This sets it to balance 0. Then at the end, the delta between the amount actually deducted and the amount that should be deducted (amount - spent) is removed from the last NFT. The issue here is that if the last NFT didn't have enough XP, its balance will be 0 and amount - spent will be != 0. Thus this will always revert when the last NFT doesn't have enough XP. The last NFT is also always the latest one which will always have the least XP making this more likely.

## Recommendation
Similar to the recommendation in H-02: Consider redesigning the design used here. Another possible way is removing a proportional amount from each NFT (amount * nft balance)/total rewards, Then iterating over the NFTs again from the top removing the delta (amount - spent) from the first possible one.
