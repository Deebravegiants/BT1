# [M] The proposer can be impeded from submitting a p...

## Summary
Severity: Medium
Chain: Smart contract
Component: Alchemix
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Alchemix/30685%20-%20%5BSC%20-%20Medium%5D%20The%20proposer%20can%20be%20impeded%20from%20submitting%20a%20p....md
Type: immunefi-boost

## Details
Target: https://github.com/alchemix-finance/alchemix-v2-dao/blob/main/src/AlchemixGovernor.sol

## Description

## Brief/Intro

The `propose` function verifies the minimum votes required for a valid proposal by checking if the number of votes obtained by `_msgSender()` within the last block timestamp is greater than or equal to the current `proposalThreshold()` value. However, it is susceptible to exploitation by an attacker who can manipulate and inflate the `proposalThreshold()` value, thereby preventing any user from successfully proposing a valid proposal.

## Vulnerability Details

In the `propose` function, there exists a verification mechanism ensuring that the `msg.sender` possesses adequate quorum votes to initiate a proposal, denoted by the condition `getVotes(_msgSender(), block.timestamp - 1) >= proposalThreshold()`. Here, the `getVotes()` function retrieves the number of votes at `block.timestamp - 1`, while the `proposalThreshold()` is calculated as follows: `(token.getPastTotalSupply(block.timestamp) * proposalNumerator) / PROPOSAL_DENOMINATOR`. Notably, `getPastTotalSupply()` fetches the `totalSupply` at the specified `block.timestamp`.

Consider the following hypothetical scenario:

1. Bob intends to propose a proposal.
2. At timestamp `x`, Bob garners 110 votes.
3. At timestamp `x + 1`, the actual `proposalThreshold` is set at 100 votes.
4. However, Alice opposes Bob's proposal.
5. Alice manipulates the `proposalThreshold` by either locking or depositing assets into an already locked position, thereby ensuring that `getVotes(bob, x) < proposalThreshold()`. Consequently, Bob's proposal transaction fails, leading to a revert.

This scenario underscores a vulnerability where an adversary, in this case, Alice, exploits the system by artificially inflating the `proposalThreshold`, effectively obstructing legitimate proposals such as Bob's from succeeding.

## Impact Details

Opposing an user from proposing by manipulating the `totalSupply`

## References

https://github.com/alchemix-finance/alchemix-v2-dao/blob/f1007439ad3a32e412468c4c42f62f676822dc1f/src/AlchemixGovernor.sol#L45-L47 https://github.com/alchemix-finance/alchemix-v2-dao/blob/f1007439ad3a32e412468c4c42f62f676822dc1f/src/governance/L2Governor.sol#L309-L312

## Proof of Concept

`Test :`

```solidity
// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.15;

```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Alchemix/30685%20-%20%5BSC%20-%20Medium%5D%20The%20proposer%20can%20be%20impeded%20from%20submitting%20a%20p....md_
