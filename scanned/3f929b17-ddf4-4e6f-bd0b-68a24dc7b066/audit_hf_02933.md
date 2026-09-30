# [M] Choosing winner can be manipulated

## Summary
Severity: Medium
Contest weight: 0.3716
Dataset id: 16279
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocols offers users the ability to enter a raffle by buying tickets. The problem is that the winners of the raffle are input by the owner.
```solidity
uint256 id)
    public
    onlyOwner
{
    for (uint256 i = 0; i < _raffleWinners.length; i++) { // iterate over input array
        isWinnerOf[_raffleWinners[i]][id] = true; // set winner to true
    }
}
```
This is problematic since the owner can chose winners.

## Recommendation
Use Chainlink VRF instead to chose the winners.
