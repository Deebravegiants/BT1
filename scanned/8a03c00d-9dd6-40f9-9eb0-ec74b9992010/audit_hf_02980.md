# [M] Fee on transfer tokens

## Summary
Severity: Medium
Contest weight: 0.4059
Dataset id: 16605
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The bridge contract will not work properly with a fee on transfer tokens:
1. User A bridges a fee on transfer Token A from Mainnet to Rollover R1 for amount X.
2. In that case X-fees will be received by bridge contract on Mainnet but the deposit receipt of the full amount X will be stored in Merkle.
3. The amount is claimed in R1 and a new TokenPair for Token A is generated and the full amount X is minted to User A
4. Now the full amount is bridged back again to Mainnet
5. When a claim is made on Mainnet then the contract tries to transfer amount X but since it received the amount X-fees it will use the amount from other users, which eventually causes DOS for other users using the same token

## Recommendation
Use the exact amount which is transferred to the contract which can be obtained using below sample code:
```solidity
uint256 balanceBefore = IERC20Upgradeable(token).balanceOf(address(this));
IERC20Upgradeable(token).safeTransferFrom(address(msg.sender), address(this), amount);
uint256 balanceAfter = IERC20Upgradeable(token).balanceOf(address(this));
uint256 transferedAmount = balanceAfter - balanceBefore;
// if you dont want to support fee on transfer token use below:
require(transferedAmount == amount, ...);
// use transferedAmount if you want to support fee on transfer token
```
Polygon-Hermez: Solved in PR 87. To protect against reentrancy with erc777 tokens, a check for reentrancy MUST be added.
Solved in PR 91.
