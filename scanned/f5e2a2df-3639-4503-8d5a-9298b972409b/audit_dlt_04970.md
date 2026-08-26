# [H] Users can lose funds when calling `extendLock()`

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/71
Type: sherlock-finding

## Details
yixxas

high

# Users can lose funds when calling `extendLock()`

## Summary
User that tries to extend their lock duration will have their tokens burned in some cases. This also causes them to be unable to withdraw their original deposit tokens.

## Vulnerability Detail

1. `extendLock()` checks for the new duration with `uint256 duration = maxLockDuration.min(uint256(userDeposit.end - block.timestamp) + increaseDuration)`
2. `mintAmount` is then calculated with `uint256 mintAmount = userDeposit.amount * getMultiplier(duration) / 1e18`
3. It then compares the previously minted amount with this new amount and mint or burn depending on the difference.

This calculation will cause user to lose tokens when the duration they extend is less than the amount of time passed. I illustrate this with a simple example.

A user first `deposit()` some amount and with duration of `1 year` and mints `x_num_of_tokens` depending on the curve. Now, right before the lock ends, at `0.99999 year`, this same user chooses to call `extendLock()` for `1 week`. The new duration calculated is `maxLockDuration.min(uint256(userDeposit.end - block.timestamp) + increaseDuration)` and this would be very close to `increaseDuration` which is 1 week in our case. `mintAmount` is calculated with this 1 week duration. Assuming curve does not change, the previously calculated `mintAmount` using `1 year` is much higher than this new one using `1 week`. End result is that `0.99999 year`'s worth of user's token is burnt. Now, user will not even be able to withdraw their original deposit tokens without the pool tokens as it will revert due to `_burn()` in `withdraw()`.

## Impact
Users who call `extendLock()` will lose their funds. How much of it depends on the point in time in which they calls it. The closer it is to expiration, the more funds are lost.

## Code Snippet

[TimeLockPool.sol#L148](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L148)
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
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/71_
