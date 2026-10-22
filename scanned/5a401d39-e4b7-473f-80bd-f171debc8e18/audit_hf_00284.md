# [M] [WP-H3] `L1Migrator.sol#migrateETH`

## Summary
Severity: Medium
Contest weight: 0.5557
Dataset id: 1442
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
uint256 amount = IBridgeMinter(bridgeMinterAddr).withdrawETHToL1Migrator();
```

`L1Migrator.sol#migrateETH()` will call `IBridgeMinter(bridgeMinterAddr).withdrawETHToL1Migrator()` to withdraw ETH from `BridgeMinter`.

However, the current implementation of `L1Migrator` is unable to receive ETH.

```solidity
(bool ok, ) = l1MigratorAddr.call.value(address(this).balance)("");
```

A contract receiving Ether must have at least one of the functions below:

  * `receive() external payable`
  * `fallback() external payable`

`receive()` is called if `msg.data` is empty, otherwise `fallback()` is called.

Because `L1Migrator` implement neither `receive()` or `fallback()`, the `call` at L94 will always revert.

## Recommendation
Add `receive() external payable {}` in `L1Migrator`.

Severity: 2 (Med)

We’ll fix this, but noting that the funds are recoverable because the BridgeMinter can set a new L1Migrator that does have the receive() function which is why the suggested severity is 2 (Med).

[yondonfu (Livepeer) resolved](https://github.com/code-423n4/2022-01-livepeer-findings/issues/198#issuecomment-1021379439):

Fixed in <https://github.com/livepeer/arbitrum-lpt-bridge/pull/50>

Agree with sponsor, these funds are recoverable. However, the warden has identified a DOS attack, which is a valid `medium` severity issue.
