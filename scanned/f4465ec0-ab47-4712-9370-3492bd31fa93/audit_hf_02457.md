# [M] Incorrect Pending Dividends Calculation in Dividends

## Summary
Severity: Medium
Contest weight: 0.4240
Dataset id: 13163
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function pendingDividendsAmount(
    address token,
    address userAddress
) external view returns (uint256) {
    if (totalAllocation == 0) {
        return 0;
    }
    DividendsInfo storage dividendsInfo_ = dividendsInfo[token];
    uint256 accDividendsPerShare = dividendsInfo_.accDividendsPerShare;
    uint256 lastUpdateTime = dividendsInfo_.lastUpdateTime;
    uint256 dividendAmountPerSecond_ = _dividendsAmountPerSecond(token);
    // check if the current cycle has changed since last update
    if (_currentBlockTimestamp() > nextCycleStartTime()) {
        // get remaining rewards from last cycle
        accDividendsPerShare += (nextCycleStartTime() - lastUpdateTime) * ((dividendAmountPerSecond_ * 1e16) / totalAllocation);
        lastUpdateTime = nextCycleStartTime();
        dividendAmountPerSecond_ = ((dividendsInfo_.pendingAmount * dividendsInfo_.cycleDividendsPercent) / 100) / _cycleDurationSeconds;
        // get pending rewards from current cycle
        accDividendsPerShare += (((_currentBlockTimestamp() - lastUpdateTime) * dividendAmountPerSecond_) * 1e16) / totalAllocation;
    }
    Public
    return ((usersAllocation[userAddress] * accDividendsPerShare) / 1e18) - (users[token][userAddress].rewardDebt + users[token][userAddress].pendingDividends);
}
```

## Recommendation
Revise the above routine to properly compute the pending dividends amount.
