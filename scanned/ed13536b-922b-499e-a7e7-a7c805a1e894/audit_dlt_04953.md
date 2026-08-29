# [H] Maximum duration multiplier can be forced for lock amount increase

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/118
Type: sherlock-finding

## Details
hyh

high

# Maximum duration multiplier can be forced for lock amount increase

## Summary

Duration multiplier is calculated based on the sender's lock data, while the amount actually received is locked for the receiver's lock period.

This provides a surface for the manipulation of locking the increaseLock() amount with the big multiplier, while it's actually locked for the small duration.

## Vulnerability Detail

Bob the attacker can create two accounts, lock a small amount, say `1 USDC`, with the first for the `maxLockDuration`, then lock some amount, say the same `1 USDC`, with the second account for the `MIN_LOCK_DURATION`, which is only 10 minutes.

Then Bob calls `increaseLock(id, second, 1e6 USDC)` from the first account, locking the whole amount for `MIN_LOCK_DURATION` with the maximum multiplier from `maxLockDuration`.

## Impact

Net impact here is reward stealing from all other users, as the shares being issued to the attacker will be substantially inflated. This way the severity is high.

## Code Snippet

Currently `_msgSender()`'s deposit is used to obtain the lock's end time:

https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L197-L222

```solidity
    function increaseLock(uint256 _depositId, address _receiver, uint256 _increaseAmount) external {
        // Check if actually increasing
        if (_increaseAmount == 0) {
            revert ZeroAmountError();
        }

        Deposit memory userDeposit = depositsOf[_msgSender()][_depositId];

        // Only can extend if it has not expired
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/118_
