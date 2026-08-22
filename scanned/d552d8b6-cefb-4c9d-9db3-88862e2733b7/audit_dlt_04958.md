# [H] extendLock function in TimeLockPool contract overwrites previously accumulated token shares

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/110
Type: sherlock-finding

## Details
ElKu

high

# extendLock function in TimeLockPool contract overwrites previously accumulated token shares

## Summary

When the user calls the `extendLock` function to extend the deposit expiry timestamp, the contract calculates the new amount of shares based on the time for which it is getting extended. The tokens accumulated so far gets overwritten and ignored. 

## Vulnerability Detail

Let's take an example:
1. `Alice` deposits 1000 tokens for a duration of 3 years.
2. The contract mints, lets say 1200 tokens(based on `getMultiplier` function's return value) on her behalf. We assume that `getMultiplier` returns a value of 1.2 when the input duration is 3 years.
3. At the end of the 3rd year, before the deposit was going to get expired, `Alice` calls the `extendLock` function and passes `_increaseDuration` as 2 years. Meaning she want to extend it for a further 2 years. In total she would have deposited for 5 years.
4. Looking at the [extendLock](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L148-L184) code:
```solidity
	uint256 increaseDuration = _increaseDuration.max(MIN_LOCK_DURATION);
        uint256 duration = maxLockDuration.min(uint256(userDeposit.end - block.timestamp) + increaseDuration);
        uint256 mintAmount = userDeposit.amount * getMultiplier(duration) / 1e18;
```
We can calculate that:
`increaseDuration` = 2 years.
`duration` = min(4 years, 0 +2 years) = 2 years.
Lets say: `getMultiplier(2 years)` = 1.1.
Then `mintAmount` = 1000 * 1.1 = 1100. 

This freshly calculated `mintAmount` is compared with the current number of shares `Alice` has:
```solidity
	if (mintAmount > userDeposit.shareAmount) {
            depositsOf[_msgSender()][_depositId].shareAmount =  mintAmount;
            _mint(_msgSender(), mintAmount - userDeposit.shareAmount);
        // If the new amount is less then burn that difference
        } else if (mintAmount < userDeposit.shareAmount) {
            depositsOf[_msgSender()][_depositId].shareAmount =  mintAmount;
            _burn(_msgSender(), userDeposit.shareAmount - mintAmount);
        }
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/110_
