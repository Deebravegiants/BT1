# [M] `safeTransferFrom` in `TransferHelper` is not `safeTransferFrom`

## Summary
Severity: Medium
Contest weight: 0.4103
Dataset id: 741
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A non standard ERC20 token would always raise error when calling `_safeTransferFrom`. If a user creates a USDT/DAI pool and deposit into the pool he would find out there’s never a counterpart deposit. See `TransferHelper.sol` [#L19](https://github.com/code-423n4/2021-07-wildcredit/blob/82c48d73fd27a9d4d5d4a395b3affcef4ef6c5c8/contracts/TransferHelper.sol#L19).

`TransferHelper` does not uses `SafeERC20` library as the function name implies.

A sample POC:

```solidity
usdt.functions.approve(lending_pair.address, deposit_amount).transact({'from': w3.eth.accounts[0]})
lending_pair.functions.deposit(w3.eth.accounts[0], usdt.address, deposit_amount).transact({'from': w3.eth.accounts[0]})
```

Error Message:

```
Error: Transaction reverted: function returned an unexpected amount of data
    at LendingPair._safeTransferFrom (contracts/TransferHelper.sol:20)
    at LendingPair.deposit (contracts/LendingPair.sol:95)
```

Recommend using `openzeppelin` `SafeERC20` in `transferHelper` (and any other contract that uses IERC20).

This can effect deposits so it’s a medium risk.

## Recommendation
No recommendation
