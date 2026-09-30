# [M] `UpdateExpirattionPeriod`

## Summary
Severity: Medium
Contest weight: 0.7073
Dataset id: 22132
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Safe cannot reduce `expirationPeriod` to a `newExpirationPeriod` when
    
    currentTimeStamp < timestamp[id] + expirationPeriod and
    currentTimeStamp >= timestamp[id] + newExpirationPeriod

where `id` is the `hash` of `updateExpirationPeriod()` and `timestamp[id]` is the timestamp when the `id` can be executed.

Safe should be able to update the `expirationPeriod` to any values >= `MIN_DELAY` by scheduling the `updateExpirationPeriod()` and later execute from `timelock` when the operation is ready (before the expiry).
    
    require(newPeriod >= MIN_DELAY, "Timelock: delay out of bounds");

But the protocol has overlooked the situation and added an reduntant check inside [_afterCall()](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1009-L1015) which is executed at the end of [_execute()](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L608).
    
```solidity
function _afterCall(bytes32 id) private {
    /// unreachable state because removing the proposal id from the
    /// _liveProposals set prevents this function from being called on the
    /// same id twice
    require(isOperationReady(id), "Timelock: operation is not ready"); //@audit
    timestamps[id] = _DONE_TIMESTAMP;
}
```

Here the `isOperationReady(id)` will be executed with the `newExpirationPeriod`.  
[code](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L399-L404)
    
```solidity
function isOperationReady(bytes32 id) public view returns (bool) {
    /// cache timestamp, save up to 2 extra SLOADs
    uint256 timestamp = timestamps[id];
    return timestamp > _DONE_TIMESTAMP && timestamp <= block.timestamp
        && timestamp + expirationPeriod > block.timestamp;
}
```

There it is checking whether the `currentTimestamp` is less than the `timestamp` + `updated EpirationPeriod` instead of the `actual expirationPeriod`.

## Recommendation
```solidity
function _afterCall(bytes32 id) private {
    //no need to check
    timestamps[id] = _DONE_TIMESTAMP;
}
```

Seems like this is a valid issue, but it’s valid only if you execute the proposal more than min delay after the transaction becomes executable and you are lowering the expiration period.

The title is misleading because you can execute this operation, but you just have to execute it within the new expiration period.

Feels more like a low severity than a medium.

I need to think about it a bit more, but fundamentally it seems to be something that the owner would cause to themselves.

With a similar point to [issue #21](https://github.com/code-423n4/2024-10-kleidi-findings/issues/21) this is an operative mistake that the user can make.

Because this is a gotcha, where under valid use no harm would be done, I think the finding is best categorized as QA.

After running the test, and reviewing the code, I see the issue.  
The new expiration is being used to validate the executed function.  
I see that this is a valid bug and am leaning towards raising the severity to Medium.

I agree that this is a valid finding, so now we’re just talking about impact and severity. The solution for the end user is just execute the transaction before the new expiration period takes place. We can warn on the UI about this.

@Alex the Entreprenerd - Will leave severity of finding to your judgement.

The finding is a bit of an edge case, when changing a proposal expiration to a smaller value, the OZ reentrancy guard will use the expiration that was newly set, causing the execution to revert.

Fundamentally given this specific scenario, a proposal will not be executable, this leads me to agree with Medium severity.
