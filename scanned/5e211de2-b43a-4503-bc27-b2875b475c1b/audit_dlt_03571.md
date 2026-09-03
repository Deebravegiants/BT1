# [M] UpdateExpirattionPeriod() cannot be execute when the newExpirationPeriod is less than currentExpirationPeriod.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-10-kleidi
Published: 2024-10-27
Source: https://github.com/code-423n4/2024-10-kleidi-findings/issues/9
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L608
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1009-L1015
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L399-L404


# Vulnerability details

## Description

Safe cannot reduce  `expirationPeriod` to a `newExpirationPeriod` when

    currentTimeStamp < timestamp[id] +  expirationPeriod and
    currentTimeStamp >= timestamp[id] +  newExpirationPeriod
    

 where `id` is the `hash` of `updateExpirationPeriod()` and `timestamp[id]` is the timestamp when the `id` can be executed.


Safe shuold be able to update the `expirationPeriod` to any values >= `MIN_DELAY` by scheduling the `updateExpirationPeriod()` and later execute from `timelock` when the operation is ready (before the expiry).

```solidity
    require(newPeriod >= MIN_DELAY, "Timelock: delay out of bounds");
```

But the protocol has overlooked the situation and added an reduntant  check inside [_afterCall()](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1009-L1015) which is executed at the end of [_execute()](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L608).

```solidity
    function _afterCall(bytes32 id) private {
        /// unreachable state because removing the proposal id from the
        /// _liveProposals set prevents this function from being called on the
        /// same id twice
        require(isOperationReady(id), "Timelock: operation is not ready"); //@audit
        timestamps[id] = _DONE_TIMESTAMP;
    }
```


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-10-kleidi-findings/issues/9_
