# [M] `bps2Uint()` precision not enough when `totalVotingPower` becomes large

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-frankendao
Published: 2022-11-16
Source: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/59
Type: sherlock-finding

## Details
__141345__

medium

# `bps2Uint()` precision not enough when `totalVotingPower` becomes large

## Summary

When `totalVotingPower` is high after some time, `proposalThreshold()` and `quorumVotes()` can lose granularity due to integer rounding issue.


## Vulnerability Detail

As more and more token minted, the `totalVotingPower` will gradually increase, eventually grow above 20000. 
```solidity
    function getTotalVotingPower() public view returns (uint) {
      return totalTokenVotingPower + getCommunityVotingPower(address(type(uint160).max));
    }
```

As users `stake`, `totalTokenVotingPower` will increase
```solidity
  function _stake(uint[] calldata _tokenIds, uint _unlockTime) internal {
    // ...
        totalTokenVotingPower += newVotingPower;
    // ...
    }
```

As user delegate votes, and `castVote()`, `totalCommunityScoreData.votes` can also increase.
```solidity
  function _castVote() internal {
    // ...
        ++totalCommunityScoreData.votes;
    // ...
    }

  function _delegate() internal {
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/59_
