# [C] Calling returnLoserTicketXPs will fail

## Summary
Severity: Critical
Contest weight: 0.4683
Dataset id: 16292
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a raffle finishes the owner will call returnLoserTicketXPs which will return the XP to the participants that didn't win. This will in turn call addXP to do the XP state changes:
```solidity
uint256 paid = 0;
uint256 payPerNFT = amount / stakedNFTs[msg.sender].length;
```
The issue is that returnLoserTicketXPs can only be called by owner:
```solidity
function returnLoserTicketXPs(uint256 id) public onlyOwner {
```
thus stakedNFTs[msg.sender].length will be 0 and the division will revert. Thus the XP can never be returned back to the stakers. At best the owner could stake an NFT, but then the calculation would be wrong as they could need to stake different numbers of NFT to match what the users have. However, fixing this in the easy way, changing msg.sender to _address opens up a pretty dangerous griefing possibility. Since a user could unstake their NFT before the call to returnLoserTicketXPs. Causing the same divide by zero DoS.

## Recommendation
Consider using the NFT balance of the _address and checking that the user still has NFTs staked:
```solidity
// - uint256 payPerNFT = amount / stakedNFTs[msg.sender].length;
if (stakedNFTs[_address].length == 0) {
    return;
}
uint256 payPerNFT = amount / stakedNFTs[_address].length;
```
This will forfeit the XP if the user unstakes before the returns are added.
