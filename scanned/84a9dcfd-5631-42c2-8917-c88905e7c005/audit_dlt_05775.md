# [C] VestedZeroNFT tokens can be directly stolen thr...

## Summary
Severity: Critical
Chain: Smart contract
Component: ZeroLend
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ZeroLend/29031%20-%20%5BSC%20-%20Critical%5D%20VestedZeroNFT%20tokens%20can%20be%20directly%20stolen%20thr....md
Type: immunefi-boost

## Details
Target: https://github.com/zerolend/governance

## Description

## Brief/Intro

The split() function of VestedZeroNFT allows a user to split a tokenId to two tokens, using the desired ratio. VestedZeroNFT is a vesting solution, allowing anyone to mint a vesting token who will eventually emit the entire locked funds.

## Vulnerability Details

The `split()` function lacks access-control check - essentially that the msg.sender is the owner of `tokenID`. The `msg.sender` is the one receiving the newly minted token with an arbitrary ratio. `_mint(msg.sender, ++lastTokenId);` This means anyone can pass an existing tokenID and `fraction=1` to still 99.99% of the value of a token.

## Impact Details

Anyone can steal the underlying value of vestedZeroNFTs

## Proof of concept

Since the project's test suite does not run, as indicated in chat, I've prepped a POC as a standalone contract which directly copies the `split()` function from VestedZeroNFT.

Simply deploy the SplitStealPOC contract and run `attack()` which proves anyone can steal another person's holdings.

```
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IERC165, ERC721Upgradeable, ERC721EnumerableUpgradeable} from "@openzeppelin/contracts-upgradeable/token/ERC721/extensions/ERC721EnumerableUpgradeable.sol";
import {IERC20} from "@openzeppelin/contracts/interfaces/IERC20.sol";
import {ERC20} from  "@openzeppelin/contracts/token/ERC20/ERC20.sol";

interface IVestedZeroNFT{
    function split( uint256 tokenId, uint256 fraction) external;
    function mint( address _who, uint256 _pending, uint256 _upfront, uint256 _linearDuration, uint256 _cliffDuration, uint256 _unlockDate, bool _hasPenalty, VestCategory _category) external returns (uint256);
    function init(address _zero, address _stakingBonus) external;
}

enum VestCategory {
    PRIVATE_SALE,
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ZeroLend/29031%20-%20%5BSC%20-%20Critical%5D%20VestedZeroNFT%20tokens%20can%20be%20directly%20stolen%20thr....md_
