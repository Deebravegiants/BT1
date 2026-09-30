# [C] User can inflate their XP by abusing updateXP

## Summary
Severity: Critical
Contest weight: 0.3745
Dataset id: 16291
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A lot of calls in VaronveStaking uses the updateXP modifier which syncs the XP state of the user:
```solidity
NFTs[i].balance += (
    (((block.timestamp - NFTs[i].lastBalanceUpdateTime) /
    period) *
    ((xpPerPeriod * NFTs[i].NFTXPMultiplier) +
    ((NFTs.length - 1) * bonusPerNFTStake)))
);
```
Which essentially takes the time between last update and now and then applies some modifiers. The issue is that lastBalanceUpdateTime is never updated. Hence for each call to this it will add XP since the time the user first staked the NFT. One way of abusing this is to first stake one NFT, then after a while, repeatedly stake and unstake a second NFT. This will cause updateRewardSingleNFT to be called multiple times and greatly inflate the XP for the first NFT.

## Recommendation
Consider saving the lastBalanceUpdateTime at the end of updateRewardSingleNFT:
```solidity
if (NFTs[i].NFTID == id) {
    NFTs[i].balance += (
        (((block.timestamp - NFTs[i].lastBalanceUpdateTime) /
        period) *
        ((xpPerPeriod * NFTs[i].NFTXPMultiplier) +
        ((NFTs.length - 1) * bonusPerNFTStake)))
    );
    NFTs[i].lastBalanceUpdateTime = block.timestamp;
    break;
}
```
