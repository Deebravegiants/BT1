# [H] Yield of `LiquidityReserve` can be stolen

## Summary
Severity: High
Chain: Smart contract
Component: 2022-06-yieldy
Published: 2022-06-26
Source: https://github.com/code-423n4/2022-06-yieldy-findings/issues/164
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-06-yieldy/blob/524f3b83522125fb7d4677fa7a7e5ba5a2c0fe67/src/contracts/LiquidityReserve.sol#L126
https://github.com/code-423n4/2022-06-yieldy/blob/524f3b83522125fb7d4677fa7a7e5ba5a2c0fe67/src/contracts/LiquidityReserve.sol#L176
https://github.com/code-423n4/2022-06-yieldy/blob/524f3b83522125fb7d4677fa7a7e5ba5a2c0fe67/src/contracts/LiquidityReserve.sol#L206


# Vulnerability details

## Impact
Using sandwich attacks and JIT (Just-in-time liquidity), the yield of `LiquidityReserve` could be extracted for liquidity providers.

## Proof of Concept
The yield of `LiquidityReserve` is distributed when a user calls `instantUnstakeReserve()` in `Staking`. Then, in `instantUnstake`, `totalLockedValue` increases with the fee paid by the user withdrawing. The fee is shared between all liquidity providers as they all see the value of their shares increase.

Therefore, an attacker could do the following sandwich attack when spotting a call to `instantUnstakeReserve()`.

 - In a first tx before the user call, borrow a lot of `stakingToken` and `addLiquidity`
 - The user call to instantUnstakeReserve()` leading to a fee of say `x`
 - In a second tx after the user call, `removeLiquidity` and repay the loan, taking a large proportion of the user fee

The problem here is that you can instantly add and remove liquidity without penalty, and that the yield is instantly distributed.


## Recommended Mitigation Steps
To mitigate this, you can
 - store the earned fees and distribute them across multiple blocks to make sure the attack wouldn’t be worth it
 - add a small fee when removing liquidity, which would make the attack unprofitable
 - prevent users from withdrawing before X blocks or add a locking mechanism
