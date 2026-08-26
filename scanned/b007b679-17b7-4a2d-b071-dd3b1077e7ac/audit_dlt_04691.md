# [M] [Tomo-M2] Failed proposals needs to re-propose

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-frankendao
Published: 2022-11-16
Source: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/63
Type: sherlock-finding

## Details
Tomo

medium

# [Tomo-M2] Failed proposals needs to re-propose

## Summary

Failed proposals needs to re-propose

## Vulnerability Detail

The `execute()` is used to execute the function of the approved proposal.

And this function is used for-loop to execute all functions per proposal.

Since there is no error handling for failed transactions, if one of the signatures is invalid, all transactions will return revert.

Furthermore, if the above condition is faced, the proposer need to create the same proposal again to execute it.

And there is no guarantee that the proposal will be approved either.

## Impact

If one of the signatures is invalid, the proposer needs to create the same proposal again.

## Code Snippet
https://github.com/sherlock-audit/2022-11-frankendao/blob/main/src/Governance.sol#L497-L514
```solidity
/// @notice Executes a queued proposal if eta has passed
/// @param _proposalId The id of the proposal to execute
function execute(uint256 _proposalId) external {
    // Queued means the proposal is passed, queued, and within the grace period.
    if (state(_proposalId) != ProposalState.Queued) revert InvalidStatus();

    Proposal storage proposal = proposals[_proposalId];
    proposal.executed = true;

```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/63_
