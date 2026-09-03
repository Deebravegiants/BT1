# [M] DOS attack by delegating tokens at MAX_DELEGATE...

## Summary
Severity: Medium
Chain: Smart contract
Component: Alchemix
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Alchemix/30592%20-%20%5BSC%20-%20Medium%5D%20DOS%20attack%20by%20delegating%20tokens%20at%20MAX_DELEGATE....md
Type: immunefi-boost

## Details
Target: https://github.com/alchemix-finance/alchemix-v2-dao/blob/main/src/VotingEscrow.sol

## Description

## Brief/Intro

In Alchemix v2 DAO's `VotingEscrow` contract, the `MAX_DELEGATES` limit is set to `1024`. This amount of delegates takes 25M gas to be processed,.However if the contracts are deployed on EVM chains having less than 25M gas block limit , Especially Optimism which has only 15M gas limit.There will be denial of service in system's core opeations especially during token transfer/withdrawal when there are 1024 delegated votes on a token.

## Resubmission

This report is a resubmission of Repoer#30549 but this one includes a runnable PoC whose output is also attached in the given secret gist.

## Vulnerability details

Any user can give their locked NFT balance to someone else using the "delegate" function. But in the "VotingEscrow" contract, there's a rule called MAX\_DELEGATES. It stops any address from having too many tokens.

here is the relevant code

VotingEscrow.sol

```solidity

// state variable
 Line 34   uint256 public constant MAX_DELEGATES = 1024; // avoid too much gas
...
_moveTokenDelegates() method
L1040 :                require(dstTokensOld.length + 1 <= MAX_DELEGATES, "dst would have too many tokenIds");

...
_moveAllDelegates() method

 require(dstTokensOld.length + ownerTokenCount <= MAX_DELEGATES, "dst would have too many tokenIds");

```

This rule helps stop attacks that could slow down or stop the contract.

Right now, if a user has 1024 delegated tokens, it takes about 25 million gas to move, burn, or make new tokens.

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Alchemix/30592%20-%20%5BSC%20-%20Medium%5D%20DOS%20attack%20by%20delegating%20tokens%20at%20MAX_DELEGATE....md_
