# [H] User can vote multiple times by delegating their voting power to different addresses

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-frankendao
Published: 2022-11-16
Source: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/1
Type: sherlock-finding

## Details
Ruhum

high

# User can vote multiple times by delegating their voting power to different addresses

## Summary
Users can vote, delegate and then vote again. They are able to vote as many times as they want. Because of the gas refunds, for voting, the user only has to pay for the delegation txs.

## Vulnerability Detail
User can delegate their tokens at any time. They can also do it after they've voted for a proposal. Thus, they are able to vote multiple times by just delegating to their own addresses.

## Impact
The whole governance system is broken because people have infinite votes.

## Code Snippet
After staking their tokens, the user calls [`castVote()`](https://github.com/sherlock-audit/2022-11-frankendao/blob/main/src/Governance.sol#L589-L646):
```sol
    function _castVote(address _voter, uint256 _proposalId, uint8 _support) internal returns (uint) {
        // Only Active proposals can be voted on
        if (state(_proposalId) != ProposalState.Active) revert InvalidStatus();
        
        // Only valid values for _support are 0 (against), 1 (for), and 2 (abstain)
        if (_support > 2) revert InvalidInput();

        Proposal storage proposal = proposals[_proposalId];

        // If the voter has already voted, revert        
        Receipt storage receipt = proposal.receipts[_voter];
        if (receipt.hasVoted) revert AlreadyVoted();

        // Calculate the number of votes a user is able to cast
        // This takes into account delegation and community voting power
        uint24 votes = (staking.getVotes(_voter)).toUint24();

        // Update the proposal's total voting records based on the votes
        if (_support == 0) {
            proposal.againstVotes = proposal.againstVotes + votes;
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/1_
