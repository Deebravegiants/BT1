# [H] Wrong TimeLockERC20 event emitted

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-nftx
Published: 2021-05-19
Source: https://github.com/code-423n4/2021-05-nftx-findings/issues/117
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details


## Vulnerability Details

The `Visor.timeLockERC721` function emits the `TimeLockERC20` event but should emit `TimeLockERC721` instead.

## Impact

It allows tricking the backend into registering ERC20 token transfers that never happened which could lead to serious issues when something like an accounting app uses this data.

## Recommended Mitigation Steps

Emit the correct event.
