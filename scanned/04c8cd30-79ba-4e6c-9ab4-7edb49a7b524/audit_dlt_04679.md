# [H] [High-3] Difference between the calculation of total community voting power and individual community voting power leaves the quorum in an incorrect state.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-frankendao
Published: 2022-11-16
Source: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/90
Type: sherlock-finding

## Details
curiousapple

high

# [High-3] Difference between the calculation of total community voting power and individual community voting power leaves the quorum in an incorrect state.

## Summary
[High-3] Difference between the calculation of total community voting power and individual community voting power leaves the quorum in an incorrect state.

## Vulnerability Detail
A total community voting power is updated inside the governance contract by staking contract through ``_updateTotalCommunityVotingPower``.
Which does not consider any ``communityPowerMultipliers``. 
```solidity
  function _updateTotalCommunityVotingPower(address _delegator, bool _increase) internal {
    (uint64 votes, uint64 proposalsCreated, uint64 proposalsPassed) = governance.userCommunityScoreData(_delegator);
    (uint64 totalVotes, uint64 totalProposalsCreated, uint64 totalProposalsPassed) = governance.totalCommunityScoreData();

    if (_increase) {
      governance.updateTotalCommunityScoreData(totalVotes + votes, totalProposalsCreated + proposalsCreated, totalProposalsPassed + proposalsPassed);
    } else {
      governance.updateTotalCommunityScoreData(totalVotes - votes, totalProposalsCreated - proposalsCreated, totalProposalsPassed - proposalsPassed);
    }
  }
 ``` 
 
 Whereas individual voting power does consider these multipliers.
Hence total community voting power would be considered lower than actual, making any proposal to achieve quorum before it reached.
  
 ```solidity 
 getCommunityVotingPower 
 ---------
 CommunityPowerMultipliers memory cpMultipliers = communityPowerMultipliers;

      return 
        (votes * cpMultipliers.votes / PERCENT) + 
        (proposalsCreated * cpMultipliers.proposalsCreated / PERCENT) +  // @audit this 
        (proposalsPassed * cpMultipliers.proposalsPassed / PERCENT);
  ```      

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/90_
