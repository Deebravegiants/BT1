# [H] NativeVault._startSnapshot() reverts with an arithmetic underflow when a native nodes balance decreases

## Summary
Severity: High
Contest weight: 0.9640
Dataset id: 13959
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
node.creditedNodeETH stores the cumulative amount of ETH ever held by the native node as it is increased in _updateSnapshot() by nodeBalanceWei:
```solidity
node.creditedNodeETH += snapshot.nodeBalanceWei;
```
Note that node.creditedNodeETH is not modified anywhere else in the code.
node.creditedNodeETH is used in _startSnapshot() to calculate the amount of ETH gained by the native node since the last snapshot:
```solidity
// Calculate unattributed node balance
uint256 nodeBalanceWei = node.nodeAddress.balance - node.creditedNodeETH;
```
However, when the native node transfers ETH out, its ETH balance will become smaller than node.creditedNodeETH. Afterwards, when _startSnapshot() is called, node.nodeAddress.balance - node.creditedNodeETH will revert with an underflow.
For example:
• Assume a native node holds 2 ETH. Both nodeAddress.balance and creditedNodeETH are 2e18.
• The node owner withdraws 1 ETH, which transfers 1 ETH out from the native node.
• When _startSnapshot() is called afterwards:
– nodeAddress.balance - creditedNodeETH = 1e18 - 2e18, which reverts with an underflow.
This makes it impossible for the node owner's snapshot to ever be updated. As such, his number of shares will never increase even if his total restaked balance increases from ETH rewards.

## Recommendation
creditedNodeETH should store the native node's ETH balance during the last snapshot.
In _updateSnapshot(), consider removing the line adding nodeBalanceWei to creditedNodeETH:
```solidity
- node.creditedNodeETH += snapshot.nodeBalanceWei;
```
Instead, set creditedNodeETH to the node's current balance in _startSnapshot(). Additionally, nodeBalanceWei should be 0 when the native node's ETH balance decreases:
```solidity
// Calculate unattributed node balance
- uint256 nodeBalanceWei = node.nodeAddress.balance - node.creditedNodeETH;
+ uint256 nodeBalanceWei;
+ if (node.nodeAddress.balance > node.creditedNodeETH) {
+ nodeBalanceWei = node.nodeAddress.balance - node.creditedNodeETH;
+ }
+ node.creditedNodeETH = node.nodeAddress.balance;
```
This ensures nodeBalanceWei will always be the amount of ETH received by the native node after the last snapshot.
