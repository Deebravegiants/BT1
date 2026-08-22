# [M] Proposal vote power can be easily manipulated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-arcade
Published: 2023-07-28
Source: https://github.com/code-423n4/2023-07-arcade-findings/issues/434
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/ArcadeGSCCoreVoting.sol#L32
https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/external/council/CoreVoting.sol#L172-L181
https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/external/council/CoreVoting.sol#L234-L238


# Vulnerability details

## Impact
`ArcadeGSCCoreVoting` can be a target of vote manipulation: an attacker might be able to take a huge loan (even uncollateralized) for a single block before creating a proposal.

When voting, only this single block is checked when calculating the `votingPower`: this may lead to an attacker being able to execute arbitrary proposals with minimal risks involved.

## Proof of Concept

When a proposal is created, the timestamp registered is the block before the creation. This mitigates flash loan attacks, but it's still possible to manipulate the vote with a normal loan:

```solidity
proposals[proposalCount] = Proposal(
    proposalHash,
    // Note we use blocknumber - 1 here as a flash loan mitigation.
    uint128(block.number - 1), //@audit created
    uint128(block.number + lockDuration),
    uint128(block.number + lockDuration + extraVoteTime),
    uint128(quorum),
    proposals[proposalCount].votingPower,
    uint128(lastCall)
);
```
https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/external/council/CoreVoting.sol#L172-L181

During a `vote`, the `msg.sender` voting power is queried and it will use the previous `created` field:

```solidity
for (uint256 i = 0; i < votingVaults.length; i++) {
    // ensure there are no voting vault duplicates
    for (uint256 j = i + 1; j < votingVaults.length; j++) {
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-arcade-findings/issues/434_
