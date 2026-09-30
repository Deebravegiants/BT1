# [H] Level XP multiplier isn't updated on NFT level

## Summary
Severity: High
Contest weight: 0.8717
Dataset id: 16276
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users have the ability to stake their NFTs to get XP in exchange. They can then use that XP to enter a raffle or level up their NFTs. Depending on the level of the NFT it has different multiplier bonuses. The problem is that when an NFT is level up the multiplier bonus is NOT updated.
```solidity
function levelUP(uint256 id)
    public
    nonReentrant
    isStakerOfAll(viewStakedNFTs(msg.sender))
    updateXP(msg.sender)
{
    if (stakedNFTs[msg.sender][getIndexOfItem(id)].NFTLevel == 1) {
        spendXP(levelTwoPrice, msg.sender);
        stakedNFTs[msg.sender][getIndexOfItem(id)].balance++;
    } else if (stakedNFTs[msg.sender][getIndexOfItem(id)].NFTLevel == 2) {
        spendXP(levelThreePrice, msg.sender);
        stakedNFTs[msg.sender][getIndexOfItem(id)].balance++;
    } else {
        revert("Your NFT reached max level.");
    }
}
```
There are state variables for the NFT level which are not used anywhere:
```solidity
uint256 levelTwoMultiplier = 2;
uint256 LevelThreeMultiplier = 3;
```

## Recommendation
Update NFTXPMultiplier when leveling up NFT:
```solidity
function levelUP(uint256 id)
    public
    nonReentrant
    isStakerOfAll(viewStakedNFTs(msg.sender))
    updateXP(msg.sender)
{
    if (stakedNFTs[msg.sender][getIndexOfItem(id)].NFTLevel == 1) {
        spendXP(levelTwoPrice, msg.sender);
        stakedNFTs[msg.sender][getIndexOfItem(id)].balance++;
        stakedNFTs[msg.sender][getIndexOfItem(id)].NFTXPMultiplier = levelTwoMultiplier;
    } else if (stakedNFTs[msg.sender][getIndexOfItem(id)].NFTLevel == 2) {
        spendXP(levelThreePrice, msg.sender);
        stakedNFTs[msg.sender][getIndexOfItem(id)].balance++;
        stakedNFTs[msg.sender][getIndexOfItem(id)].NFTXPMultiplier = LevelThreeMultiplier;
    } else {
        revert("Your NFT reached max level.");
    }
}
```
Varonve.md
