# [H] Staking.unstake() doesn't decrease the origi-

## Summary
Severity: High
Contest weight: 0.6146
Dataset id: 17800
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Staking.unstake() doesn't decrease the original voting power that was used in Staking.stake(). When users stake/unstake the underlying NFTs, it calculates the token voting power using getTokenVotingPower() and increases/decreases their voting power accordingly.
```solidity
function getTokenVotingPower(uint _tokenId) public override view returns (uint) {
    if (ownerOf(_tokenId) == address(0)) revert NonExistentToken();
    // If tokenId < 10000, it's a FrankenPunk, so 100/100 = a multiplier of 1
    uint multiplier = _tokenId < 10_000 ? PERCENT : monsterMultiplier;
    // evilBonus will return 0 for all FrankenMonsters, as they are not eligible for the evil bonus
    return ((baseVotes * multiplier) / PERCENT) + stakedTimeBonus[_tokenId] + evilBonus(_tokenId);
}
```
But getTokenVotingPower() uses some parameters like monsterMultiplier and baseVotes and the output would be changed for the same tokenId after the admin changed these settings. Currently, _stake() and _unstake() calculates the token voting power independently and the below scenario would be possible.
• At the first time, baseVotes=20, monsterMultiplier=50.
• A user staked a FrankenMonsters and his voting power = 10 here.
• After that, the admin changed monsterMultiplier=60.
• When a user tries to unstake the NFT, the token voting power will be 20*60/100=12 here.
• So it will revert with uint underflow here.
• After all, he can't unstake the NFT.
votesFromOwnedTokens might be updated wrongly or users can't unstake for the worst case because it doesn't decrease the same token voting power while unstaking.

## Recommendation
I think we should add a mapping like tokenVotingPower to save an original token voting power when users stake the token and decrease the same amount when they unstake.
