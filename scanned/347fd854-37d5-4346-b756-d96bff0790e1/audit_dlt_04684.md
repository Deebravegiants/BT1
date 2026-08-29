# [M] `cancel()` a proposal in the queued queue that will not be deleted from `queuedTransactions`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-frankendao
Published: 2022-11-16
Source: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/78
Type: sherlock-finding

## Details
8olidity

medium

# `cancel()` a proposal in the queued queue that will not be deleted from `queuedTransactions`

## Summary
`cancel()` a proposal in the queued queue that will not be deleted from `queuedTransactions`
## Vulnerability Detail
In the comment to `cancel()`, If the proposal is queued or executed, remove it from the Executor's queuedTransactions mapping. But we see `_removeTransactionWithQueuedOrExpiredCheck()` function

```solidity
    function _removeTransactionWithQueuedOrExpiredCheck(Proposal storage _proposal) internal {
        if (
            state(_proposal.id) == ProposalState.Queued || 
            state(_proposal.id) == ProposalState.Expired
        ) {
            for (uint256 i = 0; i < _proposal.targets.length; i++) {
                executor.cancelTransaction( //@audit 
                    _proposal.targets[i],
                    _proposal.values[i],
                    _proposal.signatures[i],
                    _proposal.calldatas[i],
                    _proposal.eta
                );
            }
        } else {
            _removeFromActiveProposals(_proposal.id);
        }
    }
```

Here will call `executor.cancelTransaction()`, we follow up function view

```solidity
    function cancelTransaction(
        address _target,
        uint256 _value,
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/78_
