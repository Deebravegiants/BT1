# [H] Missing whitelistTotalDeposited update in withdrawal flow enables DoS of presale whitelist allocation

## Summary
Severity: High
Contest weight: 0.7498
Dataset id: 8763
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function withdrawDeposit(uint256 amount) external nonReentrant {
    require(
```

The HolofairToken contract implements a two-phase presale system with separate allocation tracking for whitelist and public participants. The contract maintains several accounting variables to track deposits:
- deposits[address]: Tracks total deposits per user
- whitelistDeposits[address]: Tracks whitelist-specific deposits per user
- whitelistTotalDeposited: Global counter for all whitelist deposits
- publicTotalDeposited: Global counter for all public deposits
When users deposit ETH via the depositWhitelist() function, the contract properly updates both user-specific and global accounting variables:
```
whitelistTotalDeposited += depositAmount;
whitelistDeposits[msg.sender] += depositAmount;
```
However, in the withdrawDeposit() function, while the contract correctly updates whitelistDeposits[msg.sender] and other accounting variables, it fails to decrement the whitelistTotalDeposited global counter.

## Recommendation
Update the withdrawDeposit() function to properly decrement the whitelistTotalDeposited counter when whitelist deposits are withdrawn:
```solidity
function withdrawDeposit(uint256 amount) external nonReentrant {
    require(
```
