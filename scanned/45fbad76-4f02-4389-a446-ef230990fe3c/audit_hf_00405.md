# [M] DoS by gas limit

## Summary
Severity: Medium
Contest weight: 0.1380
Dataset id: 1793
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[LiquidityFarming.sol#L220](https://github.com/code-423n4/2022-03-biconomy/blob/main/contracts/hyphen/LiquidityFarming.sol#L220)  
[LiquidityFarming.sol#L233](https://github.com/code-423n4/2022-03-biconomy/blob/main/contracts/hyphen/LiquidityFarming.sol#L233)  

In `deposit` function it is possible to push to `nftIdsStaked` of anyone, an attacker can deposit too many nfts to another user, and when the user will try to withdraw an nft at the end of the list, they will iterate on the list and revert because of gas limit.

[HP-25: C4 Audit Fixes, Dynamic Fee Changes bcnmy/hyphen-contract#42](https://github.com/bcnmy/hyphen-contract/pull/42)

A valid concern, but I think it should be of medium severity because the victim can still withdraw NFTs one by one until reaching the necessary index because it breaks inside the loop: [LiquidityFarming.sol#L234-L235](https://github.com/code-423n4/2022-03-biconomy/blob/main/contracts/hyphen/LiquidityFarming.sol#L234-L235).

## Recommendation
No recommendation
