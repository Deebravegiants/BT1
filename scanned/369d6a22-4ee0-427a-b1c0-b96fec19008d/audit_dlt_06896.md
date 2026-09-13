# [M] Upgradable escrow contract

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-foundation
Published: 2022-03-02
Source: https://github.com/code-423n4/2022-02-foundation-findings/issues/53
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-foundation/blob/4d8c8931baffae31c7506872bf1100e1598f2754/contracts/FNDNFTMarket.sol


# Vulnerability details

## Impact
Upgradable escrow contract pose great risk to user who approved their NFT to the contract. Most popular token / NFT exchange do not require user approve their asset to admin upgradable contract.

This also increase user gas usage because they would have to revoke approval when they are done with the protocol.

## Proof of Concept
https://github.com/code-423n4/2022-02-foundation/blob/4d8c8931baffae31c7506872bf1100e1598f2754/contracts/FNDNFTMarket.sol

## Recommended Mitigation Steps
Separate the escrow contract to make it non-upgradable with a restricted set of functionality.
