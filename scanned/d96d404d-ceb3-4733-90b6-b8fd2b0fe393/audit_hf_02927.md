# [H] levelUP doesn't actually increase the level

## Summary
Severity: High
Contest weight: 0.7485
Dataset id: 16273
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calling levelUP a user looks to spend XP to level up their NFT:
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
Varonve.md However, the call never actually increases the level. As you can see on lines 130 and 133 it increases balance instead of NFTLevel. Hence the user is still spending their XP but their NFTs level is never increased and the balance increase is negligible.

## Recommendation
Consider increasing NFTLevel instead of balance:
```solidity
// - stakedNFTs[msg.sender][getIndexOfItem(id)].balance++;
+ stakedNFTs[msg.sender][getIndexOfItem(id)].NFTLevel++;
} else if (stakedNFTs[msg.sender][getIndexOfItem(id)].NFTLevel == 2) {
    spendXP(levelThreePrice, msg.sender);
// - stakedNFTs[msg.sender][getIndexOfItem(id)].balance++;
+ stakedNFTs[msg.sender][getIndexOfItem(id)].NFTLevel++;
```
