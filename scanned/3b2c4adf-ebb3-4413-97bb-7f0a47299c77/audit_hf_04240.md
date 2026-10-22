# [H] `deployWithdrawalQueue`

## Summary
Severity: High
Contest weight: 0.8976
Dataset id: 21155
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In `deployWithdrawalQueue()`, only clears `_queueOutstandingValues[lastQueueIndex]` and `_outstandingValues`, but doesn’t clear `_queueAccounting[lastQueueIndex]`.
```solidity
function deployWithdrawalQueue() external nonReentrant {
    ...

    /// @dev We move outstanding values from the pool to the queue that was just deployed.
    _queueOutstandingValues[pendingQueueIndex] = _outstandingValues;
    /// @dev We clear values of the new pending queue.
    delete _queueOutstandingValues[lastQueueIndex];
    delete _outstandingValues;
    //@audit miss delete _queueAccounting[lastQueueIndex]

    _updateLoanLastIds();

    _pendingQueueIndex = lastQueueIndex;

    // Cannot underflow because the sum of all withdrawals is never larger than totalSupply.
    unchecked {
        totalSupply -= sharesPendingWithdrawal;
    }
}
```
After this method, anyone calling `queueClaimAll()` will use this stale data `_queueAccounting[lastQueueIndex]`.

`queueClaimAll()` -> `_queueClaimAll(_pendingQueueIndex)`-> `_updatePendingWithdrawalWithQueue(_pendingQueueIndex)`
```solidity
function _updatePendingWithdrawalWithQueue(
    uint256 _idx,
    uint256 _cachedPendingQueueIndex,
    uint256[] memory _pendingWithdrawal
) private returns (uint256[] memory) {
    uint256 totalReceived = getTotalReceived[_idx];
    uint256 totalQueues = getMaxTotalWithdrawalQueues + 1;
    /// @dev Nothing to be returned
    if (totalReceived == 0) {
        return _pendingWithdrawal;
    }
    getTotalReceived[_idx] = 0;

    /// @dev We go from idx to newer queues. Each getTotalReceived is the total
    /// returned from loans for that queue. All future queues/pool also have a piece of it.
    /// X_i: Total received for queue `i`
    /// X_1  = Received * shares_1 / totalShares_1
    /// X_2 = (Received - (X_1)) * shares_2 / totalShares_2 ...
    /// Remainder goes to the pool.
    for (uint256 i; i < totalQueues;) {
        uint256 secondIdx = (_idx + i) % totalQueues;
        QueueAccounting memory queueAccounting = _queueAccounting[secondIdx];
        if (queueAccounting.thisQueueFraction == 0) {
            unchecked {
                ++i;
            }
            continue;
        }
        /// @dev We looped around.
        if (secondIdx == _cachedPendingQueueIndex + 1) {
            break;
        }
        uint256 pendingForQueue = totalReceived.mulDivDown(queueAccounting.thisQueueFraction, PRINCIPAL_PRECISION);
        totalReceived -= pendingForQueue;

        _pendingWithdrawal[secondIdx] = pendingForQueue;
        unchecked {
            ++i;
        }
    }
    return _pendingWithdrawal;
}
```

## Recommendation
```solidity
function deployWithdrawalQueue() external nonReentrant {
    ...

    /// @dev We move outstaning values from the pool to the queue that was just deployed.
    _queueOutstandingValues[pendingQueueIndex] = _outstandingValues;
    /// @dev We clear values of the new pending queue.
    delete _queueOutstandingValues[lastQueueIndex];
    delete _queueAccounting[lastQueueIndex];
    delete _outstandingValues;

    _updateLoanLastIds();

    _pendingQueueIndex = lastQueueIndex;

    // Cannot underflow because the sum of all withdrawals is never larger than totalSupply.
    unchecked {
        totalSupply -= sharesPendingWithdrawal;
    }
}
```
