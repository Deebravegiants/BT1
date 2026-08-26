# [H] Rewards can be stolen via lock duration extension and reduction

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/55
Type: sherlock-finding

## Details
Jeiwan

high

# Rewards can be stolen via lock duration extension and reduction

## Summary
In the [TimeLockPool contract](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L11), users deposit and lock funds for a certain duration and get pro-rata amounts of shares in exchange. The longer the duration the more shares they get. The amount of shares a user holds determines the amount of [rewards tokens they can claim](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/base/BasePool.sol#L100).

The [extendLock](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L148) function allows depositors to extend or reduce the lock duration of their funds. This function allows malicious actors to extend a lock duration to the maximal value before [reward tokens are distributed](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/base/BasePool.sol#L95-L98) and reduce it to the minimal value right after claiming their share of rewards. This allows to steal rewards from honest users who locked their funds for longer durations.
## Vulnerability Detail
The root cause of the vulnerability is that the [extendLock](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L148) function allows to reduce a lock duration at any time:
```solidity
function extendLock(uint256 _depositId, uint256 _increaseDuration) external {
    // Check if actually increasing
    if (_increaseDuration == 0) {
        revert ZeroDurationError();
    }

    Deposit memory userDeposit = depositsOf[_msgSender()][_depositId];

    // Only can extend if it has not expired
    if (block.timestamp >= userDeposit.end) {
        revert DepositExpiredError();
    }
    
    // Enforce min increase to prevent flash loan or MEV transaction ordering
    uint256 increaseDuration = _increaseDuration.max(MIN_LOCK_DURATION);
    
    // New duration is the time expiration plus the increase
    uint256 duration = maxLockDuration.min(uint256(userDeposit.end - block.timestamp) + increaseDuration);

    uint256 mintAmount = userDeposit.amount * getMultiplier(duration) / 1e18;

    // Multiplier curve changes with time, need to check if the mint amount is bigger, equal or smaller than the already minted
    
    // If the new amount if bigger mint the difference
    // @audit can be called with maxDuration right before distributeRewards
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/55_
