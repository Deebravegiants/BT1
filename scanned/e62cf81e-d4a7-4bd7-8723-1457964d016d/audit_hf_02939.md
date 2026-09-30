# [C] addXP subtracts XP instead of adding

## Summary
Severity: Critical
Contest weight: 0.3655
Dataset id: 16290
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When addXP is called it will add XP back to NFTs:
```solidity
if (stakedNFTs[_address][i].balance >= payPerNFT) {
    stakedNFTs[_address][i].balance -= payPerNFT;
    paid += payPerNFT;
} else {
    stakedNFTs[_address][i].balance = 0;
    paid += stakedNFTs[_address][i].balance;
}
```
However there's a mistake here, on line 164 it subtracts the sum instead of adding it. Causing the NFT to lose XP instead of gaining.

## Recommendation
Consider redesigning addXP and simply add payPerNFT to each NFT:
```solidity
for (uint256 i = 0; i < stakedNFTs[_address].length; i++) {
    // - if (stakedNFTs[_address][i].balance >= payPerNFT) {
    // - stakedNFTs[_address][i].balance -= payPerNFT;
    // - paid += payPerNFT;
    // - } else {
    // - stakedNFTs[_address][i].balance = 0;
    // - paid += stakedNFTs[_address][i].balance;
    stakedNFTs[_address][i].balance += payPerNFT;
    paid += payPerNFT;
    // As the check was only there to protect from underflow.
}
```
