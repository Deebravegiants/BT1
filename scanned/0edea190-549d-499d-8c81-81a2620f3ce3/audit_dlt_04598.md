# [M] There is no delay in executorship's propose/accept logic

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/89
Type: sherlock-finding

## Details
hyh

medium

# There is no delay in executorship's propose/accept logic

## Summary

TieredOwnership implementation of the two step role transfer process lacks a major detail: there is no time delay in-between the nomination of a new executor and the actual promotion to the role.

## Vulnerability Detail

Without a delay users will not be able to react to the change of the executor role holder.

Two-step process is crucial not only by being mutual, i.e. requiring both current and new executors to act, but by the introduction of a period of time between proposing a new actor and implementing the change, so all the users of the protocol be able to act on it, if needed.

## Impact

FeeBuyback users will not be able to react to the Executor role holder change, which can lead to the loss of funds the FeeBuyback contract holds as the role has full access to its balance.

Setting the severity to medium due to prerequisites: a new malicious executor needs to trick the old prudent one to nominate or to use a vulnerability to run the nomination with old executor account.

## Code Snippet

nominateExecutor() and acceptExecutorship() can be run instantly by the collided old and new executors:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/TieredOwnership.sol#L59-L80

```solidity
    /**
     * @notice nominates address as new executor
     * @param newExecutor address is the new address being given executorship
     *
     * Emits a {ExecutorNominated} event.
     */
    function nominateExecutor(address newExecutor) external onlyExecutor() {
        _nominatedExecutor = newExecutor;
        emit ExecutorNominated(_nominatedExecutor);
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/89_
